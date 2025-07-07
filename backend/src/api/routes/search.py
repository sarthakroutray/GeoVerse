# Search API routes for GeoVerse
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from datetime import datetime

from ..models.request_models import (
    SearchRequest, SearchResponse, SearchResult
)
from ...retrieval.embeddings import EmbeddingManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Global embedding manager instance
embedding_manager = EmbeddingManager()


@router.post("/", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search documents using vector similarity
    
    Performs semantic search across all indexed documents and returns relevant results.
    """
    try:
        start_time = datetime.now()
        
        # Load index if not already loaded
        if embedding_manager.vector_store is None:
            embedding_manager.load_index()
        
        if embedding_manager.vector_store is None:
            raise HTTPException(status_code=503, detail="Vector store not available")
        
        # Perform search
        raw_results = embedding_manager.search(request.query, top_k=request.top_k)
        logger.info(f"Raw search returned {len(raw_results)} results")
        
        # Filter by source type if specified
        if request.source_type:
            before_filter = len(raw_results)
            
            # Handle common source type mappings since all current data has source_type=None
            # This is a temporary workaround until data ingestion is fixed
            if request.source_type in ["webpage", "web", "html", "unknown"]:
                # For now, treat these as equivalent to None since that's what we have in raw data
                target_source_type = None
            else:
                target_source_type = request.source_type
            
            # Debug: log the source types of the first few results
            logger.info(f"Sample source types in raw results: {[r.get('source_type') for r in raw_results[:3]]}")
                
            raw_results = [
                result for result in raw_results 
                if result.get('source_type') == target_source_type
            ]
            logger.info(f"Source type filter ('{request.source_type}' -> {target_source_type}): {before_filter} -> {len(raw_results)} results")
        
        # Filter by minimum score if specified
        if request.min_score is not None:
            before_filter = len(raw_results)
            # Convert min_score from 0-1 range to the actual similarity score range if needed
            # FAISS similarity scores are typically negative (smaller = more similar)
            # But we convert them to positive scores where higher = more similar
            raw_results = [
                result for result in raw_results 
                if result.get('similarity_score', 0) >= request.min_score
            ]
            logger.info(f"Min score filter ({request.min_score}): {before_filter} -> {len(raw_results)} results")
            
            # If no results and min_score is very high, log a warning
            if len(raw_results) == 0 and request.min_score > 0.8:
                logger.warning(f"Min score {request.min_score} may be too high. Consider using a lower value (0.0-0.8 range).")
        
        # Convert to SearchResult models
        search_results = []
        for result in raw_results:
            search_result = SearchResult(
                chunk_id=result.get('chunk_id', ''),
                content=result.get('content', ''),
                title=result.get('title', ''),
                url=result.get('source_url', ''),  # Map source_url to url
                score=result.get('similarity_score', 0),  # Map similarity_score to score
                source_type=result.get('source_type', 'unknown'),
                metadata=result.get('metadata', {})
            )
            search_results.append(search_result)
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        response = SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            processing_time=processing_time
        )
        
        logger.info(f"Search completed: {request.query[:50]}... - {len(search_results)} results")
        return response
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform search: {str(e)}")


@router.get("/", response_model=SearchResponse)
async def search_documents_get(
    q: str = Query(..., description="Search query (e.g., 'INSAT satellite missions')"),
    top_k: int = Query(15, ge=1, le=100, description="Number of results to return"),
    source_type: Optional[str] = Query("webpage", description="Filter by source type (webpage, unknown)"),
    min_score: Optional[float] = Query(0.5, description="Minimum relevance score (0.0-1.0, recommended: 0.3-0.7)", ge=0.0, le=1.0)
):
    """
    Search documents using GET method
    
    Alternative endpoint for searching documents using query parameters.
    Uses reasonable defaults: top_k=15, source_type=webpage, min_score=0.5
    """
    request = SearchRequest(query=q, top_k=top_k, source_type=source_type, min_score=min_score)
    return await search_documents(request)


@router.get("/similar/{document_id}")
async def find_similar_documents(
    document_id: str,
    top_k: int = Query(10, ge=1, le=50, description="Number of similar documents")
):
    """
    Find documents similar to a specific document
    
    Uses the content of the specified document to find similar documents.
    """
    try:
        start_time = datetime.now()
        
        # Load index if not already loaded
        if embedding_manager.vector_store is None:
            embedding_manager.load_index()
        
        if embedding_manager.vector_store is None:
            raise HTTPException(status_code=503, detail="Vector store not available")
        
        # Find the document by ID
        target_doc = None
        for doc in embedding_manager.document_store:
            if doc.get('chunk_id') == document_id:
                target_doc = doc
                break
        
        if not target_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Use the document's content to find similar documents
        content = target_doc.get('content', '')
        if not content:
            raise HTTPException(status_code=400, detail="Document has no content")
        
        # Perform similarity search
        raw_results = embedding_manager.search(content, top_k=top_k + 1)  # +1 to exclude self
        
        # Remove the original document from results
        filtered_results = [
            result for result in raw_results 
            if result.get('chunk_id') != document_id
        ][:top_k]
        
        # Convert to SearchResult models
        search_results = []
        for result in filtered_results:
            search_result = SearchResult(
                chunk_id=result.get('chunk_id', ''),
                content=result.get('content', ''),
                title=result.get('title', ''),
                url=result.get('source_url', ''),  # Map source_url to url
                score=result.get('similarity_score', 0),  # Map similarity_score to score
                source_type=result.get('source_type', 'unknown'),
                metadata=result.get('metadata', {})
            )
            search_results.append(search_result)
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        response = SearchResponse(
            query=f"Similar to: {target_doc.get('title', document_id)}",
            results=search_results,
            total_results=len(search_results),
            processing_time=processing_time
        )
        
        logger.info(f"Found {len(search_results)} similar documents for {document_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar documents: {str(e)}")


@router.get("/stats")
async def get_search_stats():
    """
    Get statistics about the search index
    
    Returns information about the indexed documents and vector store.
    """
    try:
        # Load index if not already loaded
        if embedding_manager.vector_store is None:
            embedding_manager.load_index()
        
        stats = embedding_manager.get_statistics()
        
        return {
            "status": "available" if embedding_manager.vector_store else "not_available",
            "timestamp": datetime.now().isoformat(),
            **stats
        }
        
    except Exception as e:
        logger.error(f"Error getting search stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get search stats: {str(e)}")


@router.post("/reindex")
async def reindex_documents():
    """
    Trigger reindexing of all documents
    
    Rebuilds the vector index from all available processed documents.
    Note: This is an expensive operation and should be used sparingly.
    """
    try:
        from ...retrieval.embeddings import load_all_processed_data
        
        # Load all processed documents
        documents = load_all_processed_data()
        
        if not documents:
            raise HTTPException(status_code=400, detail="No documents found to index")
        
        # Rebuild index
        embedding_manager.build_index(documents, force_rebuild=True)
        
        stats = embedding_manager.get_statistics()
        
        return {
            "message": "Reindexing completed successfully",
            "timestamp": datetime.now().isoformat(),
            "documents_processed": len(documents),
            **stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during reindexing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reindex documents: {str(e)}")


@router.get("/health")
async def search_health():
    """
    Health check for search service
    
    Returns the status of search-related components.
    """
    try:
        # Check if index is loaded
        index_status = "loaded" if embedding_manager.vector_store else "not_loaded"
        
        # Get basic stats if available
        stats = {}
        if embedding_manager.vector_store:
            stats = embedding_manager.get_statistics()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "index_status": index_status,
            **stats
        }
        
    except Exception as e:
        logger.error(f"Error in search health check: {e}")
        raise HTTPException(status_code=500, detail=f"Search health check failed: {str(e)}")
