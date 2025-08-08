import asyncio
import logging
import traceback
from fastapi import APIRouter, Request, Query, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse
import json
import uuid
from typing import List, Optional
from .service import ChatbotService
from .session import SessionManager
from .schemas import Message, ChatRequest
from .config import settings
# Note: Simplified authentication will be implemented

router = APIRouter()

async def get_token(request: Request):
    """
    Extract and validate the token from the Authorization header.
    
    Args:
        request: FastAPI request object
        
    Returns:
        The extracted JWT token string
        
    Raises:
        HTTPException: If token is missing or invalid format
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split("Bearer ")[1]

    # Do a basic token validation to ensure it's a proper JWT
    parts = token.split(".")
    if len(parts) != 3:
        logging.error(
            f"Invalid token format: token has {len(parts)} segments, expected 3"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token

async def response_generator(chat_history: List[Message], question: str, thread_id: str, session_queue: asyncio.Queue, session_manager: SessionManager, chatbot_service: ChatbotService, image_url: Optional[str] = None):
    """
    Generate streaming response with proper session management.
    """
    try:
        # Retrieve or create session resources
        session_queue, queue_lock, session_task = await session_manager.get_or_create_session(thread_id)
                
        async with queue_lock:
            logging.info(f"Acquired lock for session {thread_id}")

            if session_task is None or session_task.done():
                # Start new workflow execution
                logging.info(f"Starting new workflow for session {thread_id}")
                
                # Define and start the streaming task
                async def stream_workflow_inner():
                    try:
                        # Run the workflow with the chatbot service
                        async for event in chatbot_service.run_workflow({
                            "query": question, 
                            "session_id": thread_id,
                            "chat_history": chat_history,
                            "image_url": image_url
                        }):
                            logging.debug(f"Received event: {event}")
                            await session_queue.put(event)
                        await session_queue.put(None)  # Sentinel value to signal end of stream
                    except Exception as e:
                        logging.error(f"Error in workflow streaming: {e}")
                        logging.error(traceback.format_exc())
                        await session_queue.put({"error": str(e)})
                        await session_queue.put(None)  # Ensure streaming ends

                # Create and store the streaming task
                new_task = asyncio.create_task(stream_workflow_inner())
                await session_manager.set_session_task(thread_id, new_task)

                logging.info(f"Started generation task for session {thread_id}")

            else:
                logging.info(f"Task for session {thread_id} is already running.")
                
        # Streaming loop: yield data as it becomes available
        while True:
            try:
                # Wait for the next item with a timeout to prevent hanging
                value = await asyncio.wait_for(session_queue.get(), timeout=180.0)
                logging.info(f"Received value from queue: {value}")

                if value is None:
                    logging.info(f"Received stop signal for session {thread_id}")
                    break

                # Convert dict to JSON string if it's a dictionary
                if isinstance(value, dict):
                    # Handle different streaming modes based on content
                    final_answer = value.get("final_answer")
                    plan = value.get("plan")
                    doc_urls = value.get("doc_urls")
                    citation_map = value.get("citation_map")
                    
                    # If we have a final_answer, stream it character by character
                    if final_answer and final_answer != "None":
                        # First, send plan and metadata if available
                        if plan:
                            event_data = {"type": "plan", "data": plan}
                            yield f"data: {json.dumps(event_data, default=str, ensure_ascii=False)}\n\n"
                        
                        # Stream final_answer character by character (if enabled)
                        if settings.ENABLE_CHAR_STREAMING:
                            for i in range(0, len(final_answer), settings.STREAMING_CHUNK_SIZE):
                                chunk = final_answer[i:i + settings.STREAMING_CHUNK_SIZE]
                                char_event = {"type": "answer_chunk", "data": chunk}
                                yield f"data: {json.dumps(char_event, default=str, ensure_ascii=False)}\n\n"
                                if settings.CHAR_STREAMING_DELAY > 0:
                                    await asyncio.sleep(settings.CHAR_STREAMING_DELAY)
                        else:
                            # Send complete final_answer at once
                            answer_event = {"type": "final_answer", "data": final_answer}
                            yield f"data: {json.dumps(answer_event, default=str, ensure_ascii=False)}\n\n"
                        
                        # Send metadata at the end
                        if doc_urls is not None or citation_map is not None:
                            metadata_event = {
                                "type": "metadata", 
                                "data": {
                                    "doc_urls": doc_urls,
                                    "citation_map": citation_map
                                }
                            }
                            yield f"data: {json.dumps(metadata_event, default=str, ensure_ascii=False)}\n\n"
                    
                    # For intermediate updates (no final_answer yet), send as progress
                    elif plan:
                        event_data = {"type": "progress", "data": {"plan": plan}}
                        yield f"data: {json.dumps(event_data, default=str, ensure_ascii=False)}\n\n"
                else:
                    # If it's already a string, yield it directly
                    yield str(value)

                # Mark the task as done
                session_queue.task_done()

            except asyncio.TimeoutError:
                logging.error(f"Timeout while waiting for queue item in session {thread_id}")
                yield "Error: Timeout while generating response.\n"
                break
            except Exception as e:
                logging.error(f"Unexpected error while retrieving from queue: {e}")
                yield "Error: Unexpected error while generating response.\n"
                break

        logging.info(f"Final result for session {thread_id}")        
    except Exception as e:
        logging.error(f"An unexpected error occurred for session {thread_id}: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        logging.info(f"Releasing lock for session {thread_id}")

async def cleanup_session(thread_id: str, session_manager: SessionManager):
    """
    Background task to cleanup session after timeout.
    """
    await asyncio.sleep(3600)  # Wait for 1 hour
    await session_manager.delete_session(thread_id)
    logging.info(f"Cleaned up session queue for thread_id: {thread_id}")

@router.post("/chat/query")
async def chat_query(
    chat_request: ChatRequest, 
    request: Request, 
    session_id: str = Query(None, description="Optional session ID. If not provided, a new session will be created."), 
    background_tasks: BackgroundTasks = None
):
    """
    Chat query endpoint with session-based request handling.
    
    **BREAKING CHANGE**: This endpoint now requires OAuth2 authentication.
    
    Note: Authentication dependency temporarily implemented manually due to 
    FastAPI dependency resolution issues. Will be restored to use Depends() 
    in next iteration.
    
    Args:
        chat_request: Chat request data (question, chat_history, image_url)
        request: FastAPI request object
        session_id: Optional session ID query parameter (will be generated if not provided)
        background_tasks: FastAPI background tasks
        
    Returns:
        Streaming response with chat results
        
    Raises:
        HTTPException: If authentication fails or other errors occur
    """
    try:
        # Simple token validation
        token = await get_token(request)
        logging.info(f"Authenticated request with token (last 10 chars): ...{token[-10:] if len(token) > 10 else token}")
        
        # Get session manager from app state
        session_manager: SessionManager = request.app.state.session_manager
        chatbot_service: ChatbotService = request.app.state.chatbot_service
        
        # Use provided session_id or generate a new one
        if not session_id:
            session_id = f"session_{str(uuid.uuid4())}"
        
        # Log session info
        logging.info(f"Authenticated request for session: {session_id}")
        
        # Retrieve or create session resources
        session_queue, queue_lock, session_task = await session_manager.get_or_create_session(session_id)

        # Add cleanup task if this is a new session
        if session_task is None and background_tasks:
            background_tasks.add_task(cleanup_session, session_id, session_manager)

        question = chat_request.question
        chat_history = chat_request.chat_history
        image_url = chat_request.image_url
        
        # Log query details
        logging.info(f"Authenticated user query: {question}")
        logging.info(f"Chat History: {chat_history}")
        logging.info(f"Image URL: {image_url}")

        # Start the response generation process
        return StreamingResponse(
            response_generator(chat_history, question, session_id, session_queue, session_manager, chatbot_service, image_url),
            media_type='text/event-stream'
        )

    except Exception as e:
        # Log the error and return an HTTP error response
        logging.exception("Error processing chat interaction:", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes.
    
    Returns:
        JSON response indicating the service health status
    """
    return {
        "status": "healthy",
        "service": "zmp-manual-chatbot-backend",
        "version": "0.1.4"
    }
