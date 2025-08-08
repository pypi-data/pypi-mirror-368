"""
Multi-agent workflow implementation for the ZMP Manual Chatbot Backend.

This module implements the core agents that comprise the multi-agent workflow system:
- Query processing agents (rewriter, anonymizer)
- Planning agents (planner, task handler)
- Information retrieval agents (context retriever, chat history search)
- Response generation agents (answer generator, final synthesis)

Each agent is implemented as an async function that takes a PlanExecute state
and returns an updated state, following the AsyncAgentProtocol interface.
The agents work together to process user queries through a sophisticated
pipeline that includes query optimization, context retrieval, and answer synthesis.
"""

from .schemas import PlanExecute
from typing import Optional, List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import re
import json
from .mcp_client import MCPClient
from .utils import get_llm, extract_mcp_results
from pprint import pprint

def update_step_tracking(state: PlanExecute, step_name: str) -> None:
    """
    Update workflow step tracking in the PlanExecute state.
    
    This helper function maintains the current step and history of completed
    steps in the workflow state. It's used by all agents to track progress
    through the multi-agent pipeline.
    
    Args:
        state (PlanExecute): The current workflow state to update
        step_name (str): Name of the current step being executed
        
    Note:
        - Updates the 'current_step' field with the new step name
        - Appends the step to 'past_steps' list if not already present
        - Maintains chronological order of step execution
    """
    state["current_step"] = step_name
    past_steps = state.get("past_steps", [])
    if step_name not in past_steps:
        past_steps.append(step_name)
    state["past_steps"] = past_steps

def should_log_chat_history(state: PlanExecute) -> bool:
    """
    Determine if response should be logged to chat history based on quality metrics.
    
    This function implements intelligent chat history logging by evaluating multiple
    quality indicators to determine if a response contains meaningful information
    that would be valuable for future context.
    
    Args:
        state (PlanExecute): The workflow state containing the generated response
        
    Returns:
        bool: True if the response should be logged to chat history, False otherwise
        
    Quality Assessment Criteria:
        - Response has a non-empty final answer
        - LLM-generated quality score indicates valuable content (> 0.0)
        - Response is not an error message
        - Additional boost for responses with citations
        - Minimum confidence threshold for uncertain responses
        
    Example:
        if should_log_chat_history(state):
            await log_to_chat_history(state["query"], state["final_answer"])
    """
    final_answer = state.get("final_answer", "")
    quality_score = state.get("answer_quality_score", 0.0)
    answer_confidence = state.get("answer_confidence", 0.0)
    has_citations = len(state.get("citation_map", {})) > 0
    
    # Don't log if no answer
    if not final_answer or final_answer.strip() == "":
        print("[should_log_chat_history] No final answer, not logging")
        return False
    
    # Don't log error responses
    if "error occurred" in final_answer.lower():
        print("[should_log_chat_history] Detected error response, not logging")
        return False
    
    # Primary decision based on LLM quality score
    # The LLM sets quality_score to 0.0 when no relevant data is available
    if quality_score <= 0.0:
        print(f"[should_log_chat_history] LLM quality score indicates no valuable information (score: {quality_score}), not logging")
        return False
    
    # Don't log very low quality responses
    if quality_score < 0.3:
        print(f"[should_log_chat_history] Quality score too low ({quality_score}), not logging")
        return False
    
    # Log if we have citations (indicates real content was found and cited)
    if has_citations:
        print(f"[should_log_chat_history] Response has {len(state.get('citation_map', {}))} citations with quality score {quality_score}, logging")
        return True
    
    # Log if quality score indicates meaningful content (even without citations)
    if quality_score >= 0.5:
        print(f"[should_log_chat_history] High quality response (score: {quality_score}, confidence: {answer_confidence}), logging")
        return True
    
    # Log moderate quality responses if they have decent confidence
    if quality_score >= 0.3 and answer_confidence >= 0.6:
        print(f"[should_log_chat_history] Moderate quality with high confidence (score: {quality_score}, confidence: {answer_confidence}), logging")
        return True
    
    # Default: don't log low quality responses
    print(f"[should_log_chat_history] Quality score {quality_score} and confidence {answer_confidence} don't meet logging criteria, not logging")
    return False


# LLM-based Content Filtering Components
# Define a prompt template for filtering out non-relevant content from retrieved documents.
keep_only_relevant_content_prompt_template = """
You receive a query: {query} and retrieved documents: {retrieved_documents} from a vector store.

CRITICAL INSTRUCTIONS:
1. Your ONLY job is to filter out irrelevant content. Do NOT try to make connections or find broader relevance.
2. If the query asks about a specific product/technology (like APIM, ZCP, Kubernetes, Docker), ONLY keep content that EXPLICITLY mentions that specific product/technology.
3. If the retrieved documents do NOT contain the specific product/technology mentioned in the query, return "NO_RELEVANT_CONTENT_FOUND".
4. Do NOT try to connect unrelated technologies or find broader relevance.
5. Do NOT add explanations or try to be helpful - just filter the content strictly.
6. **LANGUAGE REQUIREMENT**: Always respond in the same language as the user's query. If the query is in Korean, respond in Korean. If the query is in English, respond in English. If the query is in another language, respond in that language.

Examples:
- Query: "What is APIM?" + Documents about ZCP → Return "NO_RELEVANT_CONTENT_FOUND"
- Query: "What is ZCP?" + Documents about ZCP → Return only ZCP-specific content
- Query: "How does Kubernetes work?" + Documents about Docker → Return "NO_RELEVANT_CONTENT_FOUND"

Output the filtered relevant content OR "NO_RELEVANT_CONTENT_FOUND" if no relevant content exists.
"""

# Define a Pydantic model for structured output from the LLM, specifying that the output should contain only the relevant content.
class KeepRelevantContent(BaseModel):
    relevant_content: str = Field(description="The relevant content from the retrieved documents that is relevant to the query.")

# Create a prompt template for filtering only the relevant content from retrieved documents, using the provided template string.
keep_only_relevant_content_prompt = PromptTemplate(
    template=keep_only_relevant_content_prompt_template,
    input_variables=["query", "retrieved_documents"],
)

# Create a chain that combines the prompt template, the LLM, and the structured output parser.
# The chain takes a query and retrieved documents, filters out non-relevant information,
# and returns only the relevant content as specified by the KeepRelevantContent Pydantic model.
keep_only_relevant_content_llm = get_llm()
keep_only_relevant_content_chain = (
    keep_only_relevant_content_prompt
    | keep_only_relevant_content_llm.with_structured_output(KeepRelevantContent)
)

def keep_only_relevant_content(state):
    """
    Filters and retains only the content from the retrieved documents that is relevant to the query.

    Args:
        state (dict): A dictionary containing:
            - "question": The user's query.
            - "context": The retrieved documents/content as a string.

    Returns:
        dict: A dictionary with:
            - "relevant_context": The filtered relevant content as a string.
            - "context": The original context.
            - "question": The original question.
    """
    question = state["question"]
    context = state["context"]

    # Prepare input for the LLM chain
    input_data = {
        "query": question,
        "retrieved_documents": context
    }

    print("keeping only the relevant content...")
    pprint("--------------------")

    # Invoke the LLM chain to filter out non-relevant content
    output = keep_only_relevant_content_chain.invoke(input_data)
    relevant_content = output.relevant_content

    # Ensure the result is a string (in case it's not)
    relevant_content = "".join(relevant_content)

    # Escape quotes for downstream processing
    relevant_content = relevant_content.replace('"', '\\"').replace("'", "\\'")

    return {
        "relevant_context": relevant_content,
        "context": context,
        "question": question
    }


# Query Rewriter Agent (RAG best practice)
class Rewritequery(BaseModel):
    rewritten_query: str = Field(description="The improved query optimized for vectorstore retrieval.")

rewrite_prompt_template = """You are a query re-writer that converts an input query to a better version optimized for vectorstore retrieval.

IMPORTANT: Your goal is to improve the query for retrieval while maintaining the original intent and specific terms.

Input query: {query}

Instructions:
1. Keep the original query intent and specific terms
2. If the query contains specific product names, technologies, or acronyms (like APIM, ZCP, etc.), preserve them exactly
3. Only improve the query structure for better retrieval, don't change the core topic
4. If the query is already clear and specific, return it as-is
5. Focus on making the query more searchable while keeping the original meaning

Examples:
- "What is APIM?" → "What is APIM?"
- "Tell me about ZCP" → "Tell me about ZCP"
- "How does APIM work?" → "How does APIM work?"
- "What are the features of ZCP?" → "What are the features of ZCP?"

Return the improved query that maintains the original intent and specific terms."""

rewrite_prompt = PromptTemplate(
    template=rewrite_prompt_template,
    input_variables=["query"],
)

rewrite_query_llm = get_llm()
rewrite_query_chain = rewrite_prompt | rewrite_query_llm.with_structured_output(Rewritequery)

async def query_rewriter_agent(state: PlanExecute) -> PlanExecute:
    """
    Agent: Rewrite the user query for better retrieval and update 'rewritten_query'.
    """
    result = await rewrite_query_chain.ainvoke({"query": state["query"]})
    state["rewritten_query"] = result.rewritten_query
    update_step_tracking(state, "query_rewriter")
    return state

# -----------------------------------------------
# Anonymize query Agent
# -----------------------------------------------
class Anonymizequery(BaseModel):
    anonymized_query: str = Field(description="Anonymized query.")
    mapping: str = Field(description="Mapping of original name entities to variables as JSON string.")

anonymize_query_prompt = PromptTemplate(
    template="""
You are a query anonymizer. The input you receive is a string containing several words that
construct a query {query}. Your goal is to change all name entities, solution names, and product names in the input to variables, and remember the mapping of the original names to the variables.

IMPORTANT: You should anonymize:
1. Personal names (people, companies, organizations)
2. Solution names (like APIM, ZCP, Kubernetes, etc.)
3. Product names and specific technology names
4. Any other specific named entities

Example 1:
  if the input is "who is harry potter?" the output should be "who is X?" and the mapping should be {{"X": "harry potter"}}

Example 2:
  if the input is "how did the bad guy played with the alex and rony?"
  the output should be "how did the X played with the Y and Z?" and the mapping should be {{"X": "bad guy", "Y": "alex", "Z": "rony"}}

Example 3:
  if the input is "APIM에 대해 알려줘" the output should be "X에 대해 알려줘" and the mapping should be {{"X": "APIM"}}

Example 4:
  if the input is "Tell me about ZCP and Kubernetes" the output should be "Tell me about X and Y" and the mapping should be {{"X": "ZCP", "Y": "Kubernetes"}}

You must replace all name entities, solution names, and product names in the input with variables, and remember the mapping of the original names to the variables.
Output the anonymized query and the mapping in a JSON format.
""",
    input_variables=["query"],
)
anonymize_query_llm = get_llm()
anonymize_query_chain = anonymize_query_prompt | anonymize_query_llm.with_structured_output(Anonymizequery)

async def anonymize_query_agent(state: PlanExecute) -> PlanExecute:
    # Use rewritten_query if available, otherwise fall back to original query
    query_to_anonymize = state.get("rewritten_query", state.get("query", ""))
    result = await anonymize_query_chain.ainvoke({"query": query_to_anonymize})
    state["anonymized_query"] = result.anonymized_query
    # Parse the mapping from JSON string to dictionary
    try:
        state["mapping"] = json.loads(result.mapping)
    except (json.JSONDecodeError, TypeError):
        state["mapping"] = {}
    update_step_tracking(state, "anonymize_query")
    return state

# -----------------------------------------------
# De-Anonymize Plan Agent
# -----------------------------------------------
class DeAnonymizePlan(BaseModel):
    plan: List[str] = Field(description="Plan to follow in future. with all the variables replaced with the mapped words.")

de_anonymize_plan_prompt = PromptTemplate(
    template="""
You receive a list of tasks: {plan}, where some of the words are replaced with mapped variables. 
You also receive the mapping for those variables to words {mapping}. 
Replace all the variables in the list of tasks with the mapped words. 
If no variables are present, return the original list of tasks. 
In any case, just output the updated list of tasks in a JSON format as described here, 
without any additional text apart from the JSON.
""",
    input_variables=["plan", "mapping"],
)
de_anonymize_plan_llm = get_llm()
de_anonymize_plan_chain = (
    de_anonymize_plan_prompt
    | de_anonymize_plan_llm.with_structured_output(DeAnonymizePlan)
)

async def de_anonymize_plan_agent(state: PlanExecute) -> PlanExecute:
    result = await de_anonymize_plan_chain.ainvoke({
        "plan": state["plan"],
        "mapping": state["mapping"],
    })
    state["plan"] = result.plan
    update_step_tracking(state, "de_anonymize_plan")
    return state

# -----------------------------------------------
# Planning Component for Multi-Step query Answering
# -----------------------------------------------

class Plan(BaseModel):
    steps: List[str] = Field(description="different steps to follow, should be in sorted order")

planner_prompt = PromptTemplate(
    template="""
You are a planning agent that creates a step-by-step plan to answer the user's query.

User Query: {query}

CRITICAL LANGUAGE REQUIREMENTS:
- You MUST respond in the EXACT SAME LANGUAGE as the user's query
- Analyze the user's query language and respond in that same language
- Do NOT translate or change the language
- Do NOT respond in any other language
- This is a strict requirement - you must follow the user's language exactly

Instructions:
1. Create a clear, concise plan in the SAME LANGUAGE as the user's query.
2. Each step should be actionable and relevant.
3. All reasoning and output must be in the user's language.
4. Do NOT use any other language in your response.

Generate your plan in the user's language only.
""",
    input_variables=["query"],
)
planner_llm = get_llm()
planner_chain = planner_prompt | planner_llm.with_structured_output(Plan)

async def planner_agent(state: PlanExecute) -> PlanExecute:
    query = state.get("rewritten_query", state.get("query", ""))
    print(f"[planner_agent] Original query: {query}")
    
    result = await planner_chain.ainvoke({"query": query})
    state["plan"] = result.steps
    update_step_tracking(state, "planner")
    return state

# -----------------------------------------------
# Break Down Plan Agent
# -----------------------------------------------
break_down_plan_prompt = PromptTemplate(
    template="""
You are a plan breakdown agent that refines a plan into more detailed steps.

User Query: {query}
Original Plan: {plan}

CRITICAL LANGUAGE REQUIREMENTS:
- You MUST respond in the EXACT SAME LANGUAGE as the user's query
- Analyze the user's query language and respond in that same language
- Do NOT translate or change the language
- Do NOT respond in any other language
- This is a strict requirement - you must follow the user's language exactly

Instructions:
1. Break down the plan into more detailed, actionable steps in the SAME LANGUAGE as the user's query.
2. All reasoning and output must be in the user's language.
3. Do NOT use any other language in your response.

Generate your detailed plan in the user's language only.
""",
    input_variables=["query", "plan"],
)
break_down_plan_llm = get_llm()
break_down_plan_chain = break_down_plan_prompt | break_down_plan_llm.with_structured_output(Plan)

async def break_down_plan_agent(state: PlanExecute) -> PlanExecute:
    query = state.get("rewritten_query", state.get("query", ""))
    plan = state.get("plan", [])
    print(f"[break_down_plan_agent] Processing query: {query}")
    
    result = await break_down_plan_chain.ainvoke({"query": query, "plan": plan})
    state["plan"] = result.steps
    update_step_tracking(state, "break_down_plan")
    return state

# -----------------------------------------------
# Replan Agent
# -----------------------------------------------
class ActPossibleResults(BaseModel):
    plan: Plan = Field(description="Plan to follow in future.")
    explanation: str = Field(description="Explanation of the action.")
    can_be_answered_already: bool = Field(description="Whether enough information has been gathered to generate a final answer.")

replanner_prompt = PromptTemplate(
    template="""
You are a replanning agent that evaluates whether enough information has been gathered to answer the user's query.

User Query: {query}

ORIGINAL PLAN: {plan}
STEPS COMPLETED: {past_steps}
RETRIEVED CONTEXT: {aggregated_context}

CRITICAL LANGUAGE REQUIREMENTS:
- You MUST respond in the EXACT SAME LANGUAGE as the user's query
- Analyze the user's query language and respond in that same language
- Do NOT translate or change the language
- Do NOT respond in any other language
- This is a strict requirement - you must follow the user's language exactly

All your reasoning and output must be in the user's language.

EVALUATION CRITERIA:
1. If the retrieved context contains clear, specific information that directly answers the query, set can_be_answered_already = True
2. If the context is vague, incomplete, or doesn't address the query, set can_be_answered_already = False
3. Consider the quality and relevance of the retrieved information

DECISION RULES:
- Set can_be_answered_already = True if:
  * The context clearly defines what the query is asking about (e.g., "What is X?" and context explains what X is)
  * The context provides specific details and explanations
  * The information is relevant and comprehensive
  * You can generate a complete answer from the available context
  * The context contains concrete facts, definitions, or explanations
  * **CRITICAL**: If the context is "No relevant context found." or similar, set can_be_answered_already = True

- Set can_be_answered_already = False ONLY if:
  * The context contains some information but is completely vague or general
  * The retrieved information doesn't address the query at all
  * You need more specific or detailed information that is completely missing
  * **IMPORTANT**: Do NOT set to False if the context is "No relevant context found." - this means no data exists

IMPORTANT: If the context contains ANY specific information about the query topic, even if it's not exhaustive, set can_be_answered_already = True. Do not be overly perfectionist.

**CRITICAL FOR NO DATA SCENARIOS:**
- If the context is "No relevant context found." or similar, this means no data exists for the query topic
- In this case, set can_be_answered_already = True and plan = []
- The system will generate a "no information available" response
- Do NOT try to search for more information when no data exists

If can_be_answered_already = True:
- Set plan to an empty list []
- The workflow will proceed to answer generation

If can_be_answered_already = False:
- Provide a refined plan with specific steps to gather missing information
- Focus on what specific information is still needed
- Do not repeat steps that have already been completed

Remember: The goal is to efficiently determine if we have enough information to provide a comprehensive answer to the user's query. Be decisive and don't overthink.
""",
    input_variables=["query", "plan", "past_steps", "aggregated_context"],
)
replanner_llm = get_llm()
replanner_chain = replanner_prompt | replanner_llm.with_structured_output(ActPossibleResults)

async def replan_agent(state: PlanExecute) -> PlanExecute:
    # Extract context from retrieved results
    context_parts = []
    
    # Add knowledge base results
    if state.get("retrieve_context_result"):
        for result in state["retrieve_context_result"]:
            if isinstance(result, dict):
                if "payload" in result and "content" in result["payload"]:
                    context_parts.append(f"Source: {result['payload'].get('doc_url', 'Unknown')}\nContent: {result['payload']['content']}")
                elif "content" in result:
                    context_parts.append(f"Content: {result['content']}")
    
    # Add chat history results
    if state.get("chat_history_result"):
        for result in state["chat_history_result"]:
            if isinstance(result, dict):
                if "payload" in result and "response" in result["payload"]:
                    context_parts.append(f"Previous Response: {result['payload']['response']}")
                elif "content" in result:
                    context_parts.append(f"Chat History: {result['content']}")
    
    # Combine all context
    combined_context = "\n\n".join(context_parts) if context_parts else "No relevant context found."
    
    # Check if we have any relevant results
    has_relevant_results = len(context_parts) > 0 and combined_context != "No relevant context found."
    
    # Get current query for logging and analysis
    current_query = state.get("rewritten_query", state.get("query", ""))
    
    # # Additional check: if the query is about a specific product, verify the results contain that product
    # query_lower = current_query.lower()
    
    # LLM-based semantic relevance check
    if len(combined_context) > 50:  # Only check if we have substantial context
        try:
            # Use the existing keep_only_relevant_content function for semantic relevance checking
            filter_state = {
                "question": current_query,
                "context": combined_context
            }
            
            filtered_output = keep_only_relevant_content(filter_state)
            relevant_content = filtered_output["relevant_context"]
            
            # Check if the LLM found the context irrelevant to the query
            if (relevant_content == "NO_RELEVANT_CONTENT_FOUND" or 
                "not explicitly mentioned" in relevant_content.lower() or
                "no relevant content" in relevant_content.lower()):
                print(f"[replan_agent] LLM-based semantic check: context is not relevant to query")
                print(f"[replan_agent] Query: {current_query}")
                print(f"[replan_agent] LLM relevance result: {relevant_content}")
                has_relevant_results = False
            else:
                print(f"[replan_agent] LLM-based semantic check: context is relevant to query")
        except Exception as e:
            print(f"[replan_agent] Error in LLM-based semantic relevance check: {e}")
            # Continue with existing logic if LLM check fails
    
    # If no relevant results found, set a flag for the replanner and skip LLM call
    if not has_relevant_results:
        state["no_relevant_data_found"] = True
        print(f"[replan_agent] No relevant data found for query: {current_query}")
        print(f"[replan_agent] Combined context: {combined_context[:200]}...")
        # Set plan to empty to stop the loop and proceed to final answer
        state["plan"] = []
        state["can_be_answered_already"] = True
        update_step_tracking(state, "replan")
        print("[replan_agent] Skipping LLM call - proceeding to final answer generation")
        return state
    
    # Only call LLM if we have relevant results
    query = state.get("rewritten_query", state.get("query", ""))
    plan = state.get("plan", [])
    past_steps = state.get("past_steps", [])
    # language = state.get("language", "en")
    # print(f"[replan_agent] Using language: {language}")
    
    result = await replanner_chain.ainvoke({
        "query": query,
        "plan": plan,
        "past_steps": past_steps,
        "aggregated_context": combined_context
    })
    state["plan"] = result.plan.steps
    state["can_be_answered_already"] = result.can_be_answered_already
    update_step_tracking(state, "replan")
    # Optionally: state["replan_explanation"] = result.explanation
    return state

# -----------------------------------------------
# Task Handler Agent
# -----------------------------------------------
class TaskHandlerOutput(BaseModel):
    query: str = Field(description="The query to be either retrieved from the knowledge base or chat history, or the query that should be answered from context.")
    current_context: str = Field(description="The context to be based on in order to answer the query.")
    tool: str = Field(description="The tool to be used should be either search_knowledge, search_chat_history, or answer_from_context.")

task_handler_prompt = PromptTemplate(
    template="""
You are a task handler that receives a task {curr_task} and have to decide with tool to use to execute the task.
You have the following tools at your disposal:
Tool A: search_knowledge - retrieves relevant information from the knowledge base based on a given query.
- use Tool A when you think the current task should search for information in the knowledge base.
Tool B: search_chat_history - retrieves relevant information from chat history based on a given query.
- use Tool B when you think the current task should search for information in previous chat responses.
Tool C: answer_from_context - answers a query from a given context.
- use Tool C ONLY when the current task can be answered by the aggregated context {aggregated_context}

You also receive the last tool used {last_tool}
if {last_tool} was search_knowledge, consider using other tools than Tool A.

You also have the past steps {past_steps} that you can use to make decisions and understand the context of the task.
You also have the initial user's query {query} that you can use to make decisions and understand the context of the task.
if you decide to use Tools A or B, output the query to be used for the tool and also output the relevant tool.
if you decide to use Tool C, output the query to be used for the tool, the context, and also that the tool to be used is Tool C.
""",
    input_variables=["curr_task", "aggregated_context", "last_tool", "past_steps", "query"],
)
task_handler_llm = get_llm()
task_handler_chain = task_handler_prompt | task_handler_llm.with_structured_output(TaskHandlerOutput)

async def task_handler_agent(state: PlanExecute) -> PlanExecute:
    curr_task = state["plan"][0] if state["plan"] else ""
    result = await task_handler_chain.ainvoke({
        "curr_task": curr_task,
        "aggregated_context": state.get("aggregated_context", ""),
        "last_tool": state.get("tool", ""),
        "past_steps": state.get("past_steps", []),
        "query": state.get("rewritten_query", state["query"]),
    })
    state["query_to_retrieve_or_answer"] = result.query
    state["current_context"] = result.current_context
    state["tool"] = result.tool
    update_step_tracking(state, "task_handler")
    return state

async def retrieve_context_agent(state: PlanExecute, mcp_client: Optional[MCPClient] = None) -> PlanExecute:
    """
    Agent: Retrieve context using MCP and return 'retrieve_context_result' as a unique key.
    Uses MCPClient as an async context manager for robust resource management.
    """
    query = state.get("rewritten_query", state["query"])
    original_query = state.get("query", query)
    
    if mcp_client:
        mcp_result = await mcp_client.call_tool("search_knowledge", {"query": query})
    else:
        async with MCPClient() as client:
            mcp_result = await client.call_tool("search_knowledge", {"query": query})
    
    # Use updated extract_mcp_results for new MCP server
    results = extract_mcp_results(mcp_result)
    
    # Optionally, check for errors
    if isinstance(mcp_result, dict) and not mcp_result.get("success", True):
        print(f"[retrieve_context_agent] MCP error: {mcp_result.get('error')}")
        results = []
    
    # Use LLM-based content filtering for relevance
    filtered_results = []
    doc_urls = []
    
    # Combine all retrieved content for LLM-based filtering
    all_content = []
    all_results = []
    
    for result in results:
        if isinstance(result, dict):
            payload = result.get("payload", {})
            content = payload.get("content", "")
            doc_url = payload.get("doc_url")
            
            if content and doc_url:
                all_content.append(f"Source: {doc_url}\nContent: {content}")
                all_results.append(result)
    
    if all_content:
        # Use LLM-based filtering to determine relevance
        combined_content = "\n\n".join(all_content)
        
        try:
            # Use the LLM-based content filtering
            filter_state = {
                "question": original_query,
                "context": combined_content
            }
            
            filtered_output = keep_only_relevant_content(filter_state)
            relevant_content = filtered_output["relevant_context"]
            
            # Check if the LLM found any relevant content
            if (relevant_content.strip() and 
                relevant_content != "No relevant content found." and
                relevant_content != "NO_RELEVANT_CONTENT_FOUND" and
                "not explicitly mentioned" not in relevant_content.lower()):
                # If LLM found relevant content, include the results
                filtered_results = all_results
                doc_urls = [result.get("payload", {}).get("doc_url") for result in all_results if result.get("payload", {}).get("doc_url")]
                print(f"[retrieve_context_agent] LLM filtering found relevant content for query: {original_query}")
            else:
                print(f"[retrieve_context_agent] LLM filtering found no relevant content for query: {original_query}")
                print(f"[retrieve_context_agent] Relevant content was: {relevant_content}")
                # Don't include any results if no relevant content found
                filtered_results = []
                doc_urls = []
                
        except Exception as e:
            print(f"[retrieve_context_agent] Error in LLM-based filtering: {e}")
            # Fallback to simple filtering if LLM filtering fails
            for result in all_results:
                payload = result.get("payload", {})
                content = payload.get("content", "")
                doc_url = payload.get("doc_url")
                
                # Simple relevance check as fallback
                if any(term.lower() in content.lower() for term in original_query.lower().split() if len(term) > 2):
                    filtered_results.append(result)
                    if doc_url:
                        doc_urls.append(doc_url)
    else:
        print("[retrieve_context_agent] No content found in retrieved results")
    
    # Store doc_urls in state for downstream use
    state["doc_urls"] = doc_urls
    
    # Debug logging
    print(f"[retrieve_context_agent] Original query: {original_query}")
    print(f"[retrieve_context_agent] Rewritten query: {query}")
    print(f"[retrieve_context_agent] Total results: {len(results)}")
    print(f"[retrieve_context_agent] Filtered results: {len(filtered_results)}")
    print(f"[retrieve_context_agent] Doc URLs: {doc_urls}")
    
    # Update state with results and step tracking
    state["retrieve_context_result"] = filtered_results
    state["doc_urls"] = doc_urls
    update_step_tracking(state, "retrieve_context")
    
    return state

# The following function was incorrectly named as retrieve_context_agent (duplicate). Rename to search_chat_history_agent.
async def search_chat_history_agent(state: PlanExecute, mcp_client: Optional[MCPClient] = None) -> PlanExecute:
    """
    Agent: Search chat history using MCP and return 'chat_history_result' as a unique key.
    Uses MCPClient as an async context manager for robust resource management.
    """
    query = state.get("rewritten_query", state["query"])
    original_query = state.get("query", query)
    payload = {"query": query, "n_results": 5}
    if state.get("user_id"):
        payload["user_id"] = state["user_id"]
    if mcp_client:
        mcp_result = await mcp_client.call_tool("search_chat_history", payload)
    else:
        async with MCPClient() as client:
            mcp_result = await client.call_tool("search_chat_history", payload)
    results = extract_mcp_results(mcp_result)
    if isinstance(mcp_result, dict) and not mcp_result.get("success", True):
        print(f"[search_chat_history_agent] MCP error: {mcp_result.get('error')}")
        results = []
    
    # Use LLM-based content filtering for relevance (same as retrieve_context_agent)
    filtered_results = []
    
    # Combine all retrieved content for LLM-based filtering
    all_content = []
    all_results = []
    
    for result in results:
        if isinstance(result, dict):
            payload = result.get("payload", {})
            content = payload.get("response", "") or payload.get("content", "")
            
            if content:
                all_content.append(f"Chat History: {content}")
                all_results.append(result)
    
    if all_content:
        # Use LLM-based filtering to determine relevance
        combined_content = "\n\n".join(all_content)
        
        try:
            # Use the LLM-based content filtering
            filter_state = {
                "question": original_query,
                "context": combined_content
            }
            
            filtered_output = keep_only_relevant_content(filter_state)
            relevant_content = filtered_output["relevant_context"]
            
            # Check if the LLM found any relevant content
            if (relevant_content.strip() and 
                relevant_content != "No relevant content found." and
                relevant_content != "NO_RELEVANT_CONTENT_FOUND" and
                "not explicitly mentioned" not in relevant_content.lower()):
                # If LLM found relevant content, include the results
                filtered_results = all_results
                print(f"[search_chat_history_agent] LLM filtering found relevant content for query: {original_query}")
            else:
                print(f"[search_chat_history_agent] LLM filtering found no relevant content for query: {original_query}")
                print(f"[search_chat_history_agent] Relevant content was: {relevant_content}")
                # Don't include any results if no relevant content found
                filtered_results = []
                
        except Exception as e:
            print(f"[search_chat_history_agent] Error in LLM-based filtering: {e}")
            # Fallback to simple filtering if LLM filtering fails
            for result in all_results:
                payload = result.get("payload", {})
                content = payload.get("response", "") or payload.get("content", "")
                
                # Simple relevance check as fallback
                if any(term.lower() in content.lower() for term in original_query.lower().split() if len(term) > 2):
                    filtered_results.append(result)
                    print(f"[search_chat_history_agent] Simple filtering included result for query: {original_query}")
                else:
                    print(f"[search_chat_history_agent] Simple filtering excluded result for query: {original_query}")
    else:
        print(f"[search_chat_history_agent] No chat history content found for query: {original_query}")
    
    # Update state with results and step tracking
    state["chat_history_result"] = filtered_results
    update_step_tracking(state, "search_chat_history")
    
    return state

# -----------------------------------------------
# Enhanced Answer Generation Agent
# -----------------------------------------------
class AnswerGeneration(BaseModel):
    answer: str = Field(description="The generated answer based on the retrieved context and user query.")
    confidence: float = Field(description="Confidence score for the generated answer (0.0 to 1.0).")
    sources: List[str] = Field(description="List of source documents used to generate the answer.")

answer_generation_prompt = PromptTemplate(
    template="""
You are an expert assistant that generates accurate and helpful answers based on retrieved context.

User Query: {query}

Retrieved Context:
{context}

CRITICAL LANGUAGE REQUIREMENTS:
- You MUST respond in the EXACT SAME LANGUAGE as the user's query
- Analyze the user's query language and respond in that same language
- Do NOT translate or change the language
- Do NOT respond in any other language
- This is a strict requirement - you must follow the user's language exactly

Instructions:
1. Generate a comprehensive answer based on the retrieved context
2. Use only information from the provided context - do not add external knowledge
3. Respond in the SAME LANGUAGE as the user's query
4. If the context doesn't contain enough information to answer the query, clearly state this
5. Cite specific parts of the context when relevant
6. Provide a confidence score (0.0 to 1.0) for your answer
7. List the specific sources/documents you used from the context

Generate your answer in a clear, structured format in the user's language.
""",
    input_variables=["query", "context"],
)

answer_generation_llm = get_llm()
answer_generation_chain = answer_generation_prompt | answer_generation_llm.with_structured_output(AnswerGeneration)

async def answer_agent(state: PlanExecute) -> PlanExecute:
    """
    Enhanced Agent: Generate comprehensive answer using retrieved context.
    
    Args:
        state: The shared workflow state containing retrieved context.
    
    Returns:
        Updated PlanExecute with generated answer, confidence, and sources.
    """
    query = state.get("rewritten_query", state.get("query", ""))
    
    # Extract and combine context from both retrieval sources
    context_parts = []
    
    # Add knowledge base results
    if state.get("retrieve_context_result"):
        for result in state["retrieve_context_result"]:
            if isinstance(result, dict):
                if "payload" in result and "content" in result["payload"]:
                    context_parts.append(f"Source: {result['payload'].get('doc_url', 'Unknown')}\nContent: {result['payload']['content']}")
                elif "content" in result:
                    context_parts.append(f"Content: {result['content']}")
    
    # Add chat history results
    if state.get("chat_history_result"):
        for result in state["chat_history_result"]:
            if isinstance(result, dict):
                if "payload" in result and "response" in result["payload"]:
                    context_parts.append(f"Previous Response: {result['payload']['response']}")
                elif "content" in result:
                    context_parts.append(f"Chat History: {result['content']}")
    
    # Combine all context
    combined_context = "\n\n".join(context_parts) if context_parts else "No relevant context found."
    
    try:
        # Generate answer using LLM
        result = await answer_generation_chain.ainvoke({
            "query": query,
            "context": combined_context
        })
        state["answer"] = result.answer
        state["answer_confidence"] = result.confidence
        # If LLM did not return sources, extract from retrieve_context_result
        sources = result.sources if result.sources else []
        if not sources and state.get("retrieve_context_result"):
            seen = set()
            for r in state["retrieve_context_result"]:
                if isinstance(r, dict):
                    payload = r.get("payload", {})
                    doc_url = payload.get("doc_url")
                    if doc_url and doc_url not in seen:
                        sources.append(doc_url)
                        seen.add(doc_url)
        state["sources"] = sources
        
    except Exception as e:
        print(f"Error in answer generation: {e}")
        # Fallback to a basic answer
        state["answer"] = f"Based on the available information: {combined_context[:200]}..."
        state["answer_confidence"] = 0.5
        state["sources"] = []
    
    update_step_tracking(state, "answer")
    # After answer generation, set doc_urls to unique doc_url values from retrieve_context_result
    doc_urls = []
    if state.get("retrieve_context_result"):
        seen = set()
        for r in state["retrieve_context_result"]:
            if isinstance(r, dict):
                payload = r.get("payload", {})
                doc_url = payload.get("doc_url")
                if doc_url and doc_url not in seen:
                    doc_urls.append(doc_url)
                    seen.add(doc_url)
    state["doc_urls"] = doc_urls
    return state

# -----------------------------------------------
# Enhanced Final Answer Synthesis Agent
# -----------------------------------------------
class FinalAnswerSynthesis(BaseModel):
    final_answer: str = Field(description="The comprehensive final answer synthesized from all available information.")
    summary: str = Field(description="A brief summary of the answer generation process.")
    quality_score: float = Field(description="Overall quality score for the final answer (0.0 to 1.0).")

final_answer_prompt = PromptTemplate(
    template="""
You are an expert assistant that provides comprehensive answers based on available information.

Original Query: {query}
Has Relevant Data: {has_relevant_data}

Retrieved Context:
{context}

Previous Generated Answer: {answer}
Answer Confidence: {confidence}
Sources Used: {sources}
Past Steps: {past_steps}

CRITICAL LANGUAGE REQUIREMENTS:
- You MUST respond in the EXACT SAME LANGUAGE as the user's query
- Analyze the user's query language and respond in that same language
- Do NOT translate or change the language
- Do NOT respond in any other language
- This is a strict requirement - you must follow the user's language exactly

SCENARIO-BASED INSTRUCTIONS:

**SCENARIO 1: No Relevant Data Available**
If has_relevant_data is "false" or context is "No relevant context found." or similar:
- Provide a polite response indicating no information is available about the topic
- Suggest trying a different topic or rephrasing the question
- Keep the response concise but informative
- Example: "I don't have any information about this topic in my knowledge base. Please try asking about a different topic or rephrase your question."
- Set quality_score to 0.0
- Provide a brief summary indicating no relevant data was found

**SCENARIO 2: Relevant Data Available with Citations**
If has_relevant_data is "true" and context contains relevant information:
- Provide a comprehensive answer using the provided sources
- Use inline citations with numbers in square brackets [1], [2], etc. to reference specific sources
- Only cite sources that you actually use in your answer
- If multiple sources support the same point, cite all relevant sources together like [1], [3]
- Place citations immediately after the relevant information
- There must be a source citation at the end of every paragraph
- Do not add any paragraph without at least one source at the end
- Do NOT list sources at the end of your answer
- Set quality_score based on how comprehensive and accurate the answer is (0.5 to 1.0)
- Provide a brief summary of what information was found and used

**SCENARIO 3: Context Contains Different Topic**
If the context contains information about a different topic than what was asked (e.g., ZCP content when asked about APIM):
- Respond with: "I don't have any information about this topic in my knowledge base. Please try asking about a different topic or rephrase your question."
- Set quality_score to 0.0
- Provide a brief summary indicating irrelevant data was found

IMPORTANT: Base your answer primarily on the retrieved context, not on the previous generated answer.
Respond in the user's language only.
""",
    input_variables=["query", "answer", "confidence", "sources", "context", "past_steps", "has_relevant_data"],
)

final_answer_llm = get_llm()
final_answer_chain = final_answer_prompt | final_answer_llm.with_structured_output(FinalAnswerSynthesis)

async def get_final_answer_agent(state: PlanExecute, mcp_client: Optional[MCPClient] = None) -> PlanExecute:
    """
    Enhanced Agent: Synthesize comprehensive final answer from all available information.
    Args:
        state: The shared workflow state containing all generated information.
        mcp_client: Optional MCP client for logging.
    Returns:
        Updated PlanExecute with comprehensive final answer and metadata.
    """
    query = state.get("rewritten_query", state.get("query", ""))
    print(f"[get_final_answer_agent] Original query: {query}")
    answer = state.get("answer", "No answer generated.")
    confidence = state.get("answer_confidence", 0.0)
    sources = state.get("sources", [])
    past_steps = state.get("past_steps", [])
    # --- Begin citation-style context formatting ---
    # Gather unique (doc_url, page_no) and build citation_map
    doc_page_to_citation = {}
    citation_map = {}
    source_chunks = []
    idx = 1
    if state.get("retrieve_context_result"):
        seen = set()
        for result in state["retrieve_context_result"]:
            if isinstance(result, dict):
                payload = result.get("payload", {})
                doc_url = payload.get("doc_url", None)
                content = payload.get("content", "")
                solution = payload.get("solution", "")
                page_no = payload.get("page_no", None)
                # Only assign a new citation number for unique (doc_url, page_no)
                doc_page_key = (doc_url, page_no)
                if doc_url and page_no and doc_page_key not in doc_page_to_citation:
                    # Construct S3 image URL if possible
                    page_image_url = None
                    if doc_url and solution and page_no:
                        doc_name = doc_url.rstrip("/").split("/")[-1]
                        page_image_url = f"https://s3.console.aws.amazon.com/s3/object/zmp-ai-knowledge-store/ingested_docs.cloudzcp.net/{solution}/overview/{doc_name}/{doc_name}_page{page_no}.png"
                    citation_map[str(idx)] = {
                        "solution": solution,
                        "doc_url": doc_url,
                        "page_no": page_no,
                        "page_image_url": page_image_url
                    }
                    doc_page_to_citation[doc_page_key] = str(idx)
                    idx += 1
                # Use (doc_url, page_no, content) as unique key for context
                key = (doc_url, page_no, content)
                if key not in seen and doc_url and page_no:
                    seen.add(key)
                    citation_num = doc_page_to_citation[doc_page_key]
                    source_chunks.append(f"[{citation_num}] {content}")
    formatted_context = "\n".join(source_chunks) if source_chunks else "No relevant context found."
    state["citation_map"] = citation_map
    # Set doc_urls as unique list from citation_map
    state["doc_urls"] = list({meta["doc_url"] for meta in citation_map.values()})
    # --- End citation-style context formatting ---

    # Determine if we have relevant data
    has_relevant_data = "true" if (formatted_context != "No relevant context found." and 
                                  state.get("retrieve_context_result") and 
                                  len(state.get("retrieve_context_result", [])) > 0) else "false"
    
    # Use the final_answer_chain to generate the answer
    
    try:
        print(f"[get_final_answer_agent] Has relevant data: {has_relevant_data}")
        print(f"[get_final_answer_agent] Context: {formatted_context[:100]}...")
        
        response = await final_answer_chain.ainvoke({
            "query": query,
            "answer": answer,
            "confidence": confidence,
            "sources": sources,
            "context": formatted_context,
            "past_steps": past_steps,
            "has_relevant_data": has_relevant_data
        })
        
        print(f"[get_final_answer_agent] LLM response: {response}")
        
        # Handle structured response from FinalAnswerSynthesis
        state["final_answer"] = response.final_answer
        state["answer_summary"] = response.summary
        state["answer_quality_score"] = response.quality_score
        
        # If answer_confidence wasn't set by answer_agent, use quality_score as fallback
        if not state.get("answer_confidence"):
            state["answer_confidence"] = response.quality_score
        
        # Filter citation_map to only include used citations
        used_citations = set(re.findall(r'\[(\d+)\]', state["final_answer"]))
        filtered_citation_map = {k: v for k, v in citation_map.items() if k in used_citations}
        
    except Exception as e:
        print(f"[get_final_answer_agent] Error in final answer generation: {e}")
        # Set error state
        state["final_answer"] = "An error occurred while generating the answer. Please try again."
        state["answer_summary"] = "Error in answer generation"
        state["answer_quality_score"] = 0.0
        filtered_citation_map = citation_map
    update_step_tracking(state, "get_final_answer")
    
    # Only log chat history if we provided meaningful information
    should_log = should_log_chat_history(state)
    if should_log:
        # Log chat history in background
        import asyncio
        async def log_history():
            try:
                payload = {
                    "query": state["query"],
                    "response": state.get("final_answer", "")
                }
                if state.get("user_id"):
                    payload["user_id"] = state["user_id"]
                if state.get("session_id"):
                    payload["session_id"] = state["session_id"]
                if mcp_client:
                    await mcp_client.call_tool("log_chat_history", payload)
                else:
                    async with MCPClient() as client:
                        await client.call_tool("log_chat_history", payload)
            except Exception as e:
                print(f"[log_chat_history] Error: {e}")
        
        # Create task but don't await it to avoid blocking
        try:
            asyncio.create_task(log_history())
            print("[get_final_answer_agent] Logging meaningful response to chat history")
        except Exception as e:
            print(f"[get_final_answer_agent] Error creating log task: {e}")
    else:
        print("[get_final_answer_agent] Skipping chat history logging - no meaningful information provided")
    # Always include doc_urls and filtered citation_map in the return value
    return {**state, "doc_urls": state.get("doc_urls", []), "citation_map": filtered_citation_map} 
