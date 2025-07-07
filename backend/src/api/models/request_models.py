from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message/question")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation tracking")
    top_k: int = Field(default=10, description="Number of documents to retrieve", ge=1, le=20)


class SourceDocument(BaseModel):
    title: str = Field(..., description="Document title")
    url: str = Field(..., description="Source URL")
    content_snippet: str = Field(..., description="Relevant content snippet")
    score: float = Field(..., description="Relevance score")
    # Additional fields for compatibility
    relevance_score: Optional[float] = Field(None, description="Alias for score")
    snippet: Optional[str] = Field(None, description="Alias for content_snippet")
    
    def __init__(self, **data):
        # Handle aliases
        if 'relevance_score' in data and 'score' not in data:
            data['score'] = data['relevance_score']
        if 'snippet' in data and 'content_snippet' not in data:
            data['content_snippet'] = data['snippet']
        super().__init__(**data)


class ChatResponse(BaseModel):
    query: str = Field(..., description="Original user query")
    response: str = Field(..., description="AI assistant's response")
    sources: List[SourceDocument] = Field(default=[], description="Source documents used")
    retrieved_docs_count: int = Field(..., description="Number of documents retrieved")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    model: Optional[str] = Field(None, description="Model used for generation")
    status: str = Field(default="success", description="Response status")
    error: Optional[str] = Field(None, description="Error message if any")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")


class SuggestionsRequest(BaseModel):
    context: Optional[str] = Field(None, description="Current conversation context")
    user_input: Optional[str] = Field(None, description="Partial user input")


class SuggestionsResponse(BaseModel):
    suggestions: List[str] = Field(..., description="List of suggested questions/topics")


class ConversationMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    sources: Optional[List[SourceDocument]] = Field(default=[], description="Sources for assistant messages")


class ConversationRequest(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID to retrieve")


class ConversationResponse(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[ConversationMessage] = Field(..., description="Conversation messages")
    created_at: datetime = Field(..., description="Conversation creation time")
    updated_at: datetime = Field(..., description="Last update time")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query (e.g., 'INSAT satellite missions')")
    top_k: int = Field(default=15, description="Number of results to return", ge=1, le=100)
    source_type: Optional[str] = Field(default="webpage", description="Filter by source type (webpage, unknown)")
    min_score: Optional[float] = Field(default=0.5, description="Minimum relevance score (0.0-1.0, recommended: 0.3-0.7)", ge=0.0, le=1.0)


class SearchResult(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Content text")
    title: str = Field(..., description="Document title")
    url: str = Field(..., description="Source URL")
    score: float = Field(..., description="Relevance score")
    source_type: str = Field(..., description="Type of source document")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class SearchResponse(BaseModel):
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original search query")
    processing_time: float = Field(..., description="Query processing time in seconds")
