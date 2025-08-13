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
        # Allow dynamic auto-selection if env keys exist but provider left as 'fallback'
        configured_provider = settings.llm_provider.lower()
        if configured_provider == "fallback":
            if settings.openrouter_api_key:
                configured_provider = "openrouter"
            elif settings.gemini_api_key:
                configured_provider = "gemini"
        self.llm_provider = configured_provider

        # Initialize the appropriate LLM client / model
        if self.llm_provider == "openrouter":
            if settings.openrouter_api_key:
                logger.info(f"OpenRouter API key loaded: {settings.openrouter_api_key[:10]}...")  # Only show first 10 chars for security
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
            logger.warning(f"Using fallback LLM response mode (provider: {settings.llm_provider})")
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
        # Determine how much total context we can include (for fallback or provider with small limits)
        remaining = settings.fallback_context_chars if hasattr(settings, 'fallback_context_chars') else 2000
        for i, doc in enumerate(retrieved_docs[:8], 1):  # up to 8 docs if space allows
            title = doc.get('title', 'Untitled')
            content = doc.get('content', '')
            source_url = doc.get('source_url', '')
            score = doc.get('similarity_score', 0)
            # Take a slice proportional to remaining space
            slice_len = min( min(1500, max(400, int(remaining / max(1, (8 - i + 1))))), len(content) )
            excerpt = content[:slice_len]
            remaining -= len(excerpt)
            if remaining < 0:
                remaining = 0
            context_part = f"""Document {i} (Relevance: {score:.3f}):\nTitle: {title}\nSource: {source_url}\nContent: {excerpt}{'...' if slice_len < len(content) else ''}\n"""
            context_parts.append(context_part)
            if remaining <= 200:  # stop early if almost out of quota
                break
        
        return "\n---\n".join(context_parts)
    
    def generate_response(self, query: str, context: str) -> Dict[str, any]:
        """Generate response using configured LLM provider"""
        if self.llm_provider == "openrouter":
            return self._generate_openrouter_response(query, context)
        elif self.llm_provider == "gemini":
            return self._generate_gemini_response(query, context)
        else:
            # Fallback: Generate a simple context-based response
            return self._generate_fallback_response(query, context)
    
    def _generate_openrouter_response(self, query: str, context: str) -> Dict[str, any]:
        """Generate response using OpenRouter API"""
        if self.client is None or not settings.openrouter_api_key:
            # Fall back to local response when API is not configured
            logger.warning("OpenRouter API not configured, using fallback response")
            return self._generate_fallback_response(query, context)
        
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
    
    def _generate_fallback_response(self, query: str, context: str) -> Dict[str, any]:
        """Generate a fallback response when no LLM provider is configured"""
        try:
            # Extract key information from context
            if "No relevant context found" in context or not context.strip():
                response = f"""I understand you're asking about: "{query}"
                
Unfortunately, I don't have specific information about this topic in my current database. The MOSDAC portal contains extensive data about:

• INSAT satellite missions (weather and climate data)
• Ocean observation satellites (SCATSAT, OCEANSAT)
• Atmospheric measurements and forecasts
• Earth observation products and data access

To get detailed information, you might want to:
1. Visit the MOSDAC portal directly
2. Browse the satellite mission pages
3. Check the data products section
4. Review the documentation and help sections

Would you like to ask about a specific satellite mission or data product?"""
            else:
                # Extract titles and snippets from context
                lines = context.split('\n')
                titles = [line.replace('Title: ', '') for line in lines if line.startswith('Title: ')]
                
                response = f"""Based on the available information about "{query}":

The MOSDAC database contains relevant information from {len(titles)} sources. Here's what I found:

{context[:800]}...

For more detailed information, please refer to the source documents. The MOSDAC portal provides comprehensive data about satellite missions, weather forecasts, ocean observations, and atmospheric measurements.

Would you like me to search for more specific information about any particular aspect?"""
            
            return {
                'response': response,
                'model': 'fallback',
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error in fallback response: {e}")
            return {
                'response': "I apologize, but I'm having trouble processing your request right now. Please try again later.",
                'error': str(e),
                'status': 'error'
            }

    def chat(self, query: str, top_k: int = 10) -> Dict[str, any]:
        """Main chat function that retrieves context and generates response"""
        logger.info(f"Processing query: {query}")
        
        # Retrieve relevant documents with auto-index build if needed
        try:
            loaded = self.embedding_manager.load_index()
            if not self.embedding_manager.vector_store:
                logger.info("Vector index not loaded; attempting automatic build from processed data")
                try:
                    from ..retrieval.embeddings import load_all_processed_data
                    docs = load_all_processed_data()
                    if docs:
                        self.embedding_manager.build_index(docs, force_rebuild=True)
                    else:
                        logger.warning("No documents available to build index; retrieval will be empty")
                except Exception as be:
                    logger.error(f"Auto-build of vector index failed: {be}")
            retrieved_docs = self.embedding_manager.search(query, top_k=top_k) if self.embedding_manager.vector_store else []
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            retrieved_docs = []
        
        # Format context
        context = self.format_context(retrieved_docs)
        
        # Generate response (raw)
        response_data = self.generate_response(query, context)

        # Prepare sources for citation (top 5)
        sources = []
        for doc in retrieved_docs[:5]:
            snippet_text = doc.get('content', '')
            snippet_trimmed = snippet_text[:350] + '...' if len(snippet_text) > 350 else snippet_text
            sources.append({
                'title': doc.get('title', 'Untitled'),
                'url': doc.get('source_url', ''),
                'relevance_score': doc.get('similarity_score', 0),
                'snippet': snippet_trimmed
            })

        # Conversational formatting enhancement
        formatted_response = self._format_conversational_answer(
            query=query,
            raw_answer=response_data['response'],
            retrieved_docs=retrieved_docs,
            sources=sources,
            provider=response_data.get('model') or response_data.get('status')
        )

        result = {
            'query': query,
            'response': formatted_response,
            'sources': sources,
            'retrieved_docs_count': len(retrieved_docs),
            'timestamp': datetime.now().isoformat(),
            'model': response_data.get('model'),
            'status': response_data.get('status'),
            'error': response_data.get('error')
        }
        
        if not sources:
            logger.info("Generated response with no sources (fallback mode). Suggest running /api/v1/search/reindex to build index.")
        else:
            logger.info(f"Generated response with {len(sources)} sources")
        return result

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    def _format_conversational_answer(self, query: str, raw_answer: str, retrieved_docs: List[Dict], sources: List[Dict], provider: Optional[str]) -> str:
        """Restructure the raw answer into a concise, chatbot-style reply with key points & sources."""
        try:
            # If we have no documents, return raw answer (already a fallback explanation)
            if not retrieved_docs:
                return raw_answer

            # Extract key facts (first sentence of each top doc)
            key_points = []
            for doc in retrieved_docs[:8]:
                text = doc.get('content', '')
                first_sentence = text.split('. ')
                if first_sentence:
                    fact = first_sentence[0].strip()
                    if fact and fact not in key_points:
                        key_points.append(fact[:240])
            if not key_points:
                key_points.append("Relevant contextual information retrieved from MOSDAC sources.")

            # Summarize source titles
            source_lines = []
            for i, s in enumerate(sources, 1):
                title = (s.get('title') or 'Untitled').strip()
                rel = s.get('relevance_score', 0)
                source_lines.append(f"{i}. {title} (relevance {rel:.2f})")

            # Build follow-up suggestions heuristically
            suggestions = []
            lowered_q = query.lower()
            if 'insat' in lowered_q:
                suggestions.extend([
                    "What are the primary instruments on INSAT-3D?",
                    "How does INSAT-3D support weather forecasting?",
                    "What is the difference between INSAT-3D and INSAT-3DS?"
                ])
            if 'ocean' in lowered_q or 'scatsat' in lowered_q:
                suggestions.append("Explain SCATSAT-1 wind vector retrieval.")
            if not suggestions:
                suggestions = [
                    "Ask for mission objectives",
                    "Request available data products",
                    "Compare two satellites",
                    "Ask about data access methods"
                ]

            # Clean raw answer (strip extraneous whitespace)
            raw_clean = '\n'.join([line.rstrip() for line in raw_answer.strip().splitlines() if line.strip()])

            # Compose final
            final_parts = [
                f"Answer about \"{query}\":",
                raw_clean,
                "",
                "Key points:",
            ]
            final_parts.extend([f"• {kp}" for kp in key_points])
            final_parts.append("")
            if source_lines:
                final_parts.append("Sources (top matches):")
                final_parts.extend([f"{line}" for line in source_lines])
                final_parts.append("")
            if suggestions:
                final_parts.append("You can follow up with:")
                final_parts.extend([f"- {sug}" for sug in suggestions[:4]])
            final_parts.append("")
            final_parts.append("(Generated via GeoVerse retrieval" + (f" + {provider}" if provider else "") + ")")

            return '\n'.join(final_parts)
        except Exception as e:
            logger.error(f"Formatting error: {e}")
            return raw_answer
    
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
