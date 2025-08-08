from .mcp_client import MCPClient
from langgraph.graph import StateGraph, END, START
from langgraph.errors import GraphRecursionError
from .schemas import PlanExecute
import aiofiles
from .utils import set_plan_execute, get_plan_execute
from .agents import (
    query_rewriter_agent,
    anonymize_query_agent,
    planner_agent,
    de_anonymize_plan_agent,
    break_down_plan_agent,
    task_handler_agent,
    retrieve_context_agent,
    search_chat_history_agent,
    answer_agent,
    replan_agent,
    get_final_answer_agent,
)

class ChatbotService:
    def __init__(self, mcp_client: MCPClient = None):
        self.mcp_client = mcp_client or MCPClient()
        self.workflow = None  # Will be set in async_init

    @classmethod
    async def async_init(cls, mcp_client: MCPClient = None):
        self = cls(mcp_client)
        self.workflow = self._build_workflow()
        # Save the query processing graph (optional)
        graph_image = self.workflow.get_graph().draw_mermaid_png()
        async with aiofiles.open("workflow_graph.png", "wb") as f:
            await f.write(graph_image)
        return self

    def _build_workflow(self):
        graph = StateGraph(PlanExecute)
        # Add nodes using modular agent functions
        graph.add_node("query_rewriter", query_rewriter_agent)
        graph.add_node("anonymize_query", anonymize_query_agent)
        graph.add_node("planner", planner_agent)
        graph.add_node("de_anonymize_plan", de_anonymize_plan_agent)
        graph.add_node("break_down_plan", break_down_plan_agent)
        graph.add_node("task_handler", task_handler_agent)
        graph.add_node("retrieve_context", retrieve_context_agent)
        graph.add_node("search_chat_history", search_chat_history_agent)
        graph.add_node("answer", answer_agent)
        graph.add_node("replan", replan_agent)
        graph.add_node("get_final_answer", get_final_answer_agent)
        # Set entry point
        graph.add_edge(START, "query_rewriter")
        graph.add_edge("query_rewriter", "anonymize_query")
        # Linear flow
        graph.add_edge("anonymize_query", "planner")
        graph.add_edge("planner", "de_anonymize_plan")
        graph.add_edge("de_anonymize_plan", "break_down_plan")
        graph.add_edge("break_down_plan", "task_handler")
        # Task handler branching: Route based on determined tool
        def task_handler_router(state):
            tool = state.get("tool", "")
            
            # If the task handler determined we should answer from context, go directly to answer
            if tool == "answer_from_context":
                return "answer"
            # If the task handler determined we should search knowledge base, go to retrieve_context
            elif tool == "search_knowledge":
                return "retrieve_context"
            # For search_chat_history or default, try chat history first
            else:
                return "search_chat_history"
        
        graph.add_conditional_edges(
            "task_handler",
            task_handler_router,
            {
                "retrieve_context": "retrieve_context", 
                "search_chat_history": "search_chat_history",
                "answer": "answer"
            }
        )
        # Smart sequential routing: chat_history -> answer if results found, else retrieve_context
        def chat_history_router(state):
            # Check if chat history found relevant results
            chat_results = state.get("chat_history_result", [])
            print(f"[chat_history_router] Chat results type: {type(chat_results)}, length: {len(chat_results) if isinstance(chat_results, list) else 'N/A'}")
            print(f"[chat_history_router] Chat results content: {chat_results}")
            
            if chat_results and len(chat_results) > 0:
                # Found relevant chat history, go directly to answer
                print("[chat_history_router] Found relevant chat history, routing to answer agent")
                return "answer"
            else:
                # No relevant chat history, try knowledge base
                print("[chat_history_router] No relevant chat history, routing to retrieve_context")
                return "retrieve_context"
        
        graph.add_conditional_edges(
            "search_chat_history",
            chat_history_router,
            {
                "answer": "answer",
                "retrieve_context": "retrieve_context"
            }
        )
        
        # Other nodes go directly to replan
        graph.add_edge("retrieve_context", "replan")
        graph.add_edge("answer", "replan")
        # Replan branching
        def replan_router(state):
            if state.get("can_be_answered_already"):
                return "get_final_answer"
            else:
                return "break_down_plan"
        graph.add_conditional_edges(
            "replan",
            replan_router,
            {"get_final_answer": "get_final_answer", "break_down_plan": "break_down_plan"}
        )
        # Get final answer -> END
        graph.add_edge("get_final_answer", END)
        return graph.compile()

    async def run_workflow(self, state: dict):
        session_id = state.get("session_id")
        if session_id:
            loaded_state = await get_plan_execute(session_id)
            if loaded_state:
                state.update(loaded_state)
        
        # Initialize required fields for PlanExecute TypedDict
        state.setdefault("past_steps", [])
        state.setdefault("current_step", "")
        state.setdefault("anonymized_query", "")
        state.setdefault("rewritten_query", None)
        state.setdefault("query_to_retrieve_or_answer", "")
        state.setdefault("plan", [])
        state.setdefault("mapping", {})
        state.setdefault("current_context", "")
        state.setdefault("aggregated_context", "")
        state.setdefault("tool", "")
        state.setdefault("retrieve_context_result", None)
        state.setdefault("chat_history_result", None)
        state.setdefault("answer", None)
        state.setdefault("answer_confidence", None)
        state.setdefault("sources", None)
        state.setdefault("final_answer", None)
        state.setdefault("answer_summary", None)
        state.setdefault("answer_quality_score", None)
        state.setdefault("response", "")
        
        plan = state.get("plan")
        # If plan is a string (single step), convert to list
        if isinstance(plan, str):
            plan = [plan]
        state["plan"] = plan
        try:
            async for event in self.workflow.astream(state, stream_mode="values", config={"recursion_limit": 50}):
                # Use current_step for step tracking
                current_step = event.get("current_step")
                if not current_step:
                    # Fallback: try to infer from plan or previous step
                    if plan and len(plan) > 0:
                        current_step = plan[0]
                    else:
                        current_step = None
                
                # Update past_steps in the event
                if current_step:
                    event_past_steps = event.get("past_steps", [])
                    if current_step not in event_past_steps:
                        event_past_steps.append(current_step)
                    event["past_steps"] = event_past_steps
                
                # Ensure current_step is set in the event
                if current_step:
                    event["current_step"] = current_step
                
                if session_id:
                    await set_plan_execute(session_id, event)
                yield event
        except GraphRecursionError:
            # Handle recursion limit error gracefully
            error_event = {
                "current_step": "error",
                "final_answer": "I apologize, but I encountered a processing limit while trying to answer your question. This might be due to the complexity of the query or insufficient information in my knowledge base. Please try rephrasing your question or asking about a different topic.",
                "answer_summary": "Recursion limit exceeded - providing fallback response",
                "answer_quality_score": 0.0,
                "doc_urls": [],
                "past_steps": state.get("past_steps", [])
            }
            if session_id:
                await set_plan_execute(session_id, error_event)
            yield error_event
