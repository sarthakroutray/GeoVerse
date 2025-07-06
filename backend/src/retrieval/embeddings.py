# Text embedding and vector store management
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
import hashlib

from ..utils.config import settings

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages text embeddings and vector similarity search"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self.model = None
        self.vector_store = None
        self.document_store = []
        self.index_file = Path(settings.embeddings_directory) / "mosdac.faiss"
        self.documents_file = Path(settings.embeddings_directory) / "content.json"
        self.metadata_file = Path(settings.embeddings_directory) / "metadata.json"
        
        # Ensure directory exists
        Path(settings.embeddings_directory).mkdir(parents=True, exist_ok=True)
    
    def load_model(self):
        """Load the sentence transformer model"""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts"""
        self.load_model()
        logger.info(f"Creating embeddings for {len(texts)} texts")
        
        # Create embeddings in batches to manage memory
        batch_size = 32
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(batch, convert_to_numpy=True)
            embeddings.append(batch_embeddings)
            
            if i % (batch_size * 10) == 0:
                logger.info(f"Processed {i + len(batch)} / {len(texts)} texts")
        
        embeddings = np.vstack(embeddings)
        logger.info(f"Created embeddings with shape: {embeddings.shape}")
        return embeddings
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks for better retrieval"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks
    
    def process_documents(self, documents: List[Dict]) -> List[Dict]:
        """Process documents into chunks with metadata"""
        processed_docs = []
        
        for doc in documents:
            content = doc.get('content') or doc.get('total_text', '')
            if not content:
                continue
            
            # Create chunks
            chunks = self.chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                chunk_doc = {
                    'chunk_id': f"{doc.get('url', doc.get('file_path', 'unknown'))}#chunk_{i}",
                    'content': chunk,
                    'source_url': doc.get('url') or doc.get('source_url'),
                    'title': doc.get('title', ''),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'word_count': len(chunk.split()),
                    'source_type': 'web' if 'url' in doc else 'pdf',
                    'metadata': {
                        'scraped_at': doc.get('scraped_at'),
                        'processed_at': doc.get('processed_at'),
                        'file_path': doc.get('file_path'),
                        'meta_description': doc.get('meta_description'),
                        'author': doc.get('author'),
                        'subject': doc.get('subject')
                    }
                }
                processed_docs.append(chunk_doc)
        
        logger.info(f"Processed {len(documents)} documents into {len(processed_docs)} chunks")
        return processed_docs
    
    def build_index(self, documents: List[Dict], force_rebuild: bool = False):
        """Build FAISS vector index from documents"""
        if not force_rebuild and self.index_file.exists():
            logger.info("Loading existing vector index")
            self.load_index()
            return
        
        logger.info("Building new vector index")
        
        # Process documents into chunks
        processed_docs = self.process_documents(documents)
        
        if not processed_docs:
            logger.warning("No documents to process")
            return
        
        # Extract text content for embedding
        texts = [doc['content'] for doc in processed_docs]
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.vector_store = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add embeddings to index
        self.vector_store.add(embeddings)
        
        # Store document metadata
        self.document_store = processed_docs
        
        # Save index and documents
        self.save_index()
        
        logger.info(f"Built vector index with {len(processed_docs)} documents")
    
    def save_index(self):
        """Save FAISS index and document store to disk"""
        # Save FAISS index
        faiss.write_index(self.vector_store, str(self.index_file))
        
        # Save documents
        with open(self.documents_file, 'w', encoding='utf-8') as f:
            json.dump(self.document_store, f, indent=2, ensure_ascii=False)
        
        # Save metadata
        metadata = {
            'model_name': self.model_name,
            'total_documents': len(self.document_store),
            'vector_dimension': self.vector_store.d if self.vector_store else 0,
            'index_type': 'IndexFlatIP'
        }
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved vector index to {self.index_file}")
    
    def load_index(self):
        """Load FAISS index and document store from disk"""
        if not self.index_file.exists():
            logger.warning("No saved index found")
            return False
        
        try:
            # Load FAISS index
            self.vector_store = faiss.read_index(str(self.index_file))
            
            # Load documents
            with open(self.documents_file, 'r', encoding='utf-8') as f:
                self.document_store = json.load(f)
            
            # Load metadata
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            logger.info(f"Loaded vector index with {len(self.document_store)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search for similar documents using vector similarity"""
        if self.vector_store is None:
            logger.warning("Vector store not loaded")
            return []
        
        self.load_model()
        
        # Create query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Perform search
        scores, indices = self.vector_store.search(query_embedding, top_k)
        
        # Collect results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.document_store):
                doc = self.document_store[idx].copy()
                doc['similarity_score'] = float(score)
                doc['rank'] = i + 1
                results.append(doc)
        
        logger.info(f"Found {len(results)} similar documents for query")
        return results
    
    def get_statistics(self) -> Dict:
        """Get statistics about the vector store"""
        if not self.document_store:
            return {}
        
        # Count by source type
        source_types = {}
        for doc in self.document_store:
            source_type = doc.get('source_type', 'unknown')
            source_types[source_type] = source_types.get(source_type, 0) + 1
        
        # Count unique sources
        unique_sources = len(set(doc.get('source_url', '') for doc in self.document_store))
        
        return {
            'total_chunks': len(self.document_store),
            'unique_sources': unique_sources,
            'source_types': source_types,
            'vector_dimension': self.vector_store.d if self.vector_store else 0,
            'model_name': self.model_name
        }


def load_all_processed_data() -> List[Dict]:
    """Load all processed data from various sources"""
    all_documents = []
    
    # Load scraped web content
    scraped_dir = Path(settings.raw_data_directory) / "scraped_content"
    if scraped_dir.exists():
        for json_file in scraped_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    documents = json.load(f)
                    all_documents.extend(documents)
                    logger.info(f"Loaded {len(documents)} documents from {json_file}")
            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")
    
    # Load processed PDFs
    pdf_file = Path(settings.processed_data_directory) / "pdfs" / "processed_pdfs.json"
    if pdf_file.exists():
        try:
            with open(pdf_file, 'r', encoding='utf-8') as f:
                pdf_documents = json.load(f)
                all_documents.extend(pdf_documents)
                logger.info(f"Loaded {len(pdf_documents)} PDF documents")
        except Exception as e:
            logger.error(f"Failed to load PDF documents: {e}")
    
    logger.info(f"Total loaded documents: {len(all_documents)}")
    return all_documents


if __name__ == "__main__":
    # Example usage - build embeddings from all processed data
    embedding_manager = EmbeddingManager()
    
    # Load all processed documents
    documents = load_all_processed_data()
    
    if documents:
        # Build vector index
        embedding_manager.build_index(documents, force_rebuild=True)
        
        # Test search
        results = embedding_manager.search("satellite data", top_k=5)
        for result in results:
            print(f"Score: {result['similarity_score']:.3f} - {result['title']}")
    else:
        logger.warning("No documents found to process")
