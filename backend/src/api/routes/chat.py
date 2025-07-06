# Chat API routes for GeoVerse
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging
from datetime import datetime

from ..models.request_models import (
    ChatRequest, ChatResponse, SuggestionsRequest, SuggestionsResponse,
    ConversationRequest, ConversationResponse, ConversationMessage, SourceDocument
)
from ...llm.chat_engine import chat_engine, conversation_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for conversational AI
    
    Processes user queries and returns AI-generated responses with source citations.
    """
    try:
        # Generate response using chat engine
        result = chat_engine.chat(request.message, top_k=request.top_k)
        
        # Convert sources to Pydantic models
        sources = [
            SourceDocument(
                title=source['title'],
                url=source['url'],
                relevance_score=source['relevance_score'],
                snippet=source['snippet']
            )
            for source in result['sources']
        ]
        
        # Create response
        response = ChatResponse(
            query=result['query'],
            response=result['response'],
            sources=sources,
            retrieved_docs_count=result['retrieved_docs_count'],
            timestamp=result['timestamp'],
            model=result.get('model'),
            status=result['status'],
            error=result.get('error')
        )
        
        # Save to conversation history if session_id provided
        if request.session_id:
            # Add user message
            conversation_manager.add_message(request.session_id, {
                'type': 'user',
                'content': request.message
            })
            
            # Add assistant response
            conversation_manager.add_message(request.session_id, {
                'type': 'assistant',
                'content': result['response'],
                'sources': result['sources']
            })
        
        logger.info(f"Processed chat request: {request.message[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(partial_query: str = "", limit: int = 5):
    """
    Get query suggestions based on partial input
    
    Helps users discover relevant queries about MOSDAC data.
    """
    try:
        suggestions = chat_engine.get_suggestions(partial_query)
        
        # Limit results
        if limit < len(suggestions):
            suggestions = suggestions[:limit]
        
        return SuggestionsResponse(suggestions=suggestions)
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@router.get("/conversation/{session_id}", response_model=ConversationResponse)
async def get_conversation(session_id: str):
    """
    Get conversation history for a session
    
    Retrieves the chat history for a given session ID.
    """
    try:
        messages = conversation_manager.get_conversation(session_id)
        
        # Convert to Pydantic models
        conversation_messages = []
        for msg in messages:
            sources = None
            if msg.get('sources'):
                sources = [
                    SourceDocument(
                        title=source.get('title', ''),
                        url=source.get('url', ''),
                        relevance_score=source.get('relevance_score', 0),
                        snippet=source.get('snippet', '')
                    )
                    for source in msg['sources']
                ]
            
            conversation_messages.append(ConversationMessage(
                type=msg['type'],
                content=msg['content'],
                timestamp=msg['timestamp'],
                sources=sources
            ))
        
        return ConversationResponse(
            session_id=session_id,
            messages=conversation_messages,
            message_count=len(conversation_messages)
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


@router.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """
    Clear conversation history for a session
    
    Removes all messages from the conversation history.
    """
    try:
        conversation_manager.clear_conversation(session_id)
        return {"message": f"Conversation {session_id} cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation: {str(e)}")


@router.get("/health")
async def chat_health():
    """
    Health check for chat service
    
    Returns the status of chat-related components.
    """
    try:
        # Check if embedding manager is loaded
        vector_store_status = "loaded" if chat_engine.embedding_manager.vector_store else "not_loaded"
        
        # Check if Gemini is configured
        gemini_status = "configured" if chat_engine.model else "not_configured"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "vector_store_status": vector_store_status,
            "gemini_status": gemini_status,
            "active_conversations": len(conversation_manager.conversations)
        }
        
    except Exception as e:
        logger.error(f"Error in chat health check: {e}")
        raise HTTPException(status_code=500, detail=f"Chat health check failed: {str(e)}")
