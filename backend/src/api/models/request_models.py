from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message/question")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")


class SourceDocument(BaseModel):
    title: str = Field(..., description="Document title")
    url: str = Field(..., description="Source URL")
    content_snippet: str = Field(..., description="Relevant content snippet")
    score: float = Field(..., description="Relevance score")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant's response")
    sources: List[SourceDocument] = Field(default=[], description="Source documents used")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


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
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=10, description="Number of results to return", ge=1, le=100)
    source_type: Optional[str] = Field(None, description="Filter by source type")
    min_score: Optional[float] = Field(None, description="Minimum relevance score", ge=0.0, le=1.0)


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
