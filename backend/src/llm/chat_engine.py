# LLM chat engine for generating responses using retrieved context
import google.generativeai as genai
from openai import OpenAI
from typing import List, Dict, Optional
import logging
import json
from datetime import datetime

from ..utils.config import settings
from ..retrieval.embeddings import EmbeddingManager

logger = logging.getLogger(__name__)


class ChatEngine:
    """Chat engine that combines retrieval with LLM generation"""
    
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.llm_provider = settings.llm_provider
        
        # Initialize the appropriate LLM client
        if self.llm_provider == "openrouter":
            if settings.openrouter_api_key:
                self.client = OpenAI(
                    api_key=settings.openrouter_api_key,
                    base_url=settings.openrouter_base_url
                )
                self.model_name = settings.llm_model
                logger.info(f"Initialized OpenRouter client with model: {self.model_name}")
            else:
                logger.error("OpenRouter API key not configured")
                self.client = None
        elif self.llm_provider == "gemini":
            if settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(settings.gemini_model)
                logger.info(f"Initialized Gemini client with model: {settings.gemini_model}")
            else:
                logger.error("Gemini API key not configured")
                self.model = None
        else:
            logger.error(f"Unsupported LLM provider: {self.llm_provider}")
            self.client = None
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the LLM"""
        return """You are GeoVerse, an AI assistant specialized in geospatial and earth observation data from the MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre) portal.

Your expertise includes:
- Satellite missions (INSAT, SCATSAT, etc.)
- Weather and climate data
- Ocean and atmospheric measurements
- Earth observation products
- Data access and usage

Guidelines:
1. Provide accurate, helpful information based on the provided context
2. If you don't have specific information, clearly state so
3. Include relevant citations when available
4. Explain technical concepts clearly
5. Suggest related topics or data products when appropriate
6. Always be helpful and educational

When answering:
- Start with a direct answer to the question
- Provide relevant details from the context
- Include source URLs when available
- Suggest next steps or related information if helpful"""
    
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """Format retrieved documents into context for the LLM"""
        if not retrieved_docs:
            return "No relevant context found."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs[:5], 1):  # Use top 5 results
            title = doc.get('title', 'Untitled')
            content = doc.get('content', '')
            source_url = doc.get('source_url', '')
            score = doc.get('similarity_score', 0)
            
            context_part = f"""
Document {i} (Relevance: {score:.3f}):
Title: {title}
Source: {source_url}
Content: {content[:800]}{'...' if len(content) > 800 else ''}
"""
            context_parts.append(context_part)
        
        return "\n---\n".join(context_parts)
    
    def generate_response(self, query: str, context: str) -> Dict[str, any]:
        """Generate response using configured LLM provider"""
        if self.llm_provider == "openrouter":
            return self._generate_openrouter_response(query, context)
        elif self.llm_provider == "gemini":
            return self._generate_gemini_response(query, context)
        else:
            return {
                'response': "I apologize, but no LLM provider is configured.",
                'error': "No LLM provider configured",
                'status': 'error'
            }
    
    def _generate_openrouter_response(self, query: str, context: str) -> Dict[str, any]:
        """Generate response using OpenRouter API"""
        if self.client is None:
            return {
                'response': "I apologize, but the OpenRouter service is not configured.",
                'error': "OpenRouter API not configured",
                'status': 'error'
            }
        
        try:
            # Create messages for OpenAI-compatible API
            messages = [
                {
                    "role": "system",
                    "content": """You are GeoVerse, an AI assistant specialized in geospatial and earth observation data from the MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre) portal.

Your expertise includes:
- Satellite missions (INSAT, SCATSAT, etc.)
- Weather and climate data
- Ocean and atmospheric measurements
- Earth observation products
- Data access and usage

Guidelines:
1. Provide accurate, helpful information based on the provided context
2. If you don't have specific information, clearly state so
3. Include relevant citations when available
4. Explain technical concepts clearly
5. Suggest related topics or data products when appropriate
6. Always be helpful and educational"""
                },
                {
                    "role": "user",
                    "content": f"""Context from MOSDAC database:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. Include relevant citations and source URLs when available."""
                }
            ]
            
            # Generate response using OpenRouter
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=settings.max_tokens,
                temperature=0.7
            )
            
            # Extract response text
            response_text = response.choices[0].message.content if response.choices else "I apologize, but I couldn't generate a response."
            
            return {
                'response': response_text,
                'model': self.model_name,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response with OpenRouter: {e}")
            return {
                'response': "I apologize, but I'm having trouble generating a response right now. Please try again later.",
                'error': str(e),
                'status': 'error'
            }
    
    def _generate_gemini_response(self, query: str, context: str) -> Dict[str, any]:
        """Generate response using Google Gemini API"""
        if self.model is None:
            return {
                'response': "I apologize, but the Gemini service is not configured.",
                'error': "Gemini API not configured",
                'status': 'error'
            }
        
        try:
            # Create the prompt for Gemini
            prompt = f"""You are GeoVerse, an AI assistant specialized in geospatial and earth observation data from the MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre) portal.

Your expertise includes:
- Satellite missions (INSAT, SCATSAT, etc.)
- Weather and climate data
- Ocean and atmospheric measurements
- Earth observation products
- Data access and usage

Guidelines:
1. Provide accurate, helpful information based on the provided context
2. If you don't have specific information, clearly state so
3. Include relevant citations when available
4. Explain technical concepts clearly
5. Suggest related topics or data products when appropriate
6. Always be helpful and educational

Context from MOSDAC database:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. Include relevant citations and source URLs when available."""

            # Generate response using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=settings.gemini_max_tokens,
                    temperature=settings.gemini_temperature,
                )
            )
            
            # Extract response text
            response_text = response.text if response.text else "I apologize, but I couldn't generate a response."
            
            return {
                'response': response_text,
                'model': settings.gemini_model,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response with Gemini: {e}")
            return {
                'response': "I apologize, but I'm having trouble generating a response right now. Please try again later.",
                'error': str(e),
                'status': 'error'
            }
    
    def chat(self, query: str, top_k: int = 10) -> Dict[str, any]:
        """Main chat function that retrieves context and generates response"""
        logger.info(f"Processing query: {query}")
        
        # Retrieve relevant documents
        try:
            self.embedding_manager.load_index()
            retrieved_docs = self.embedding_manager.search(query, top_k=top_k)
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            retrieved_docs = []
        
        # Format context
        context = self.format_context(retrieved_docs)
        
        # Generate response
        response_data = self.generate_response(query, context)
        
        # Prepare sources for citation
        sources = []
        for doc in retrieved_docs[:5]:
            source = {
                'title': doc.get('title', 'Untitled'),
                'url': doc.get('source_url', ''),
                'relevance_score': doc.get('similarity_score', 0),
                'snippet': doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', '')
            }
            sources.append(source)
        
        result = {
            'query': query,
            'response': response_data['response'],
            'sources': sources,
            'retrieved_docs_count': len(retrieved_docs),
            'timestamp': datetime.now().isoformat(),
            'model': response_data.get('model'),
            'status': response_data.get('status'),
            'error': response_data.get('error')
        }
        
        logger.info(f"Generated response with {len(sources)} sources")
        return result
    
    def get_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions based on partial input"""
        # Simple suggestions based on common MOSDAC topics
        suggestions = [
            "What satellite missions does MOSDAC support?",
            "How do I access sea surface temperature data?",
            "What is INSAT-3D used for?",
            "How to download ocean color data?",
            "What weather data is available?",
            "How to access SCATSAT-1 data?",
            "What is the data archival process?",
            "How to use MOSDAC web services?",
            "What atmospheric data products are available?",
            "How to access historical satellite data?"
        ]
        
        # Filter suggestions based on partial query
        if partial_query:
            filtered = [s for s in suggestions if partial_query.lower() in s.lower()]
            return filtered[:5]
        
        return suggestions[:5]


class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self):
        self.conversations = {}  # session_id -> conversation history
    
    def add_message(self, session_id: str, message: Dict[str, any]):
        """Add a message to conversation history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            **message,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_conversation(self, session_id: str) -> List[Dict[str, any]]:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]


# Global instances
chat_engine = ChatEngine()
conversation_manager = ConversationManager()


if __name__ == "__main__":
    # Example usage
    engine = ChatEngine()
    
    # Test query
    result = engine.chat("What is INSAT-3D satellite used for?")
    print(f"Query: {result['query']}")
    print(f"Response: {result['response']}")
    print(f"Sources: {len(result['sources'])}")
    
    for source in result['sources']:
        print(f"- {source['title']} (Score: {source['relevance_score']:.3f})")
