# GeoVerse Backend 🚀

FastAPI-based backend for the GeoVerse AI-powered geospatial question-answering system.

## 🎯 Overview

The backend handles data ingestion, processing, knowledge graph management, vector embeddings, and provides RESTful APIs for the React frontend.

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (metadata), Neo4j (knowledge graph)
- **Vector Store**: FAISS or ChromaDB
- **Task Queue**: Celery with Redis
- **Authentication**: JWT tokens
- **Documentation**: Automatic OpenAPI/Swagger docs

## 📁 Project Structure

```
backend/
├── src/
│   ├── ingestion/          # Data ingestion pipeline
│   ├── knowledge_graph/    # Neo4j integration
│   ├── retrieval/         # RAG functionality
│   ├── multimodal/        # Advanced content processing
│   ├── api/              # FastAPI routes and models
│   ├── llm/              # LLM integration
│   └── utils/            # Shared utilities
├── tests/                # Test suites
├── scripts/              # Utility scripts
└── config/               # Configuration files
```

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL
- Neo4j
- Redis

### Installation

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and API keys
   ```

4. **Database setup**
   ```bash
   python scripts/setup_database.py
   ```

5. **Start the server**
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Development

### Code Structure
- Follow FastAPI best practices
- Use Pydantic models for request/response validation
- Implement proper error handling and logging
- Write comprehensive tests

### Key Components

#### 1. Data Ingestion (`src/ingestion/`)
- Web scraping with Scrapy/BeautifulSoup
- PDF/DOCX processing
- Dynamic content handling with Selenium

#### 2. Knowledge Graph (`src/knowledge_graph/`)
- Entity extraction with spaCy
- Neo4j graph construction
- Relationship modeling

#### 3. Retrieval System (`src/retrieval/`)
- Vector embeddings with Sentence-Transformers
- Hybrid search (vector + knowledge graph)
- Result ranking and filtering

#### 4. API Endpoints (`src/api/`)
- `/chat` - Conversational interface
- `/search` - Direct search functionality
- `/admin` - Data management

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_api.py
```

## 📦 Deployment

### Docker
```bash
docker build -t geoverse-backend .
docker run -p 8000:8000 geoverse-backend
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `NEO4J_URI`: Neo4j database URI
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: OpenAI API key
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## 🤝 Contributing

1. Follow PEP 8 style guidelines
2. Write docstrings for all functions
3. Add tests for new functionality
4. Update API documentation
5. Use type hints consistently

## 📄 API Reference

### Chat Endpoints
- `POST /api/v1/chat` - Send message to AI assistant
- `GET /api/v1/chat/history` - Get conversation history

### Search Endpoints  
- `POST /api/v1/search` - Perform semantic search
- `GET /api/v1/search/suggestions` - Get search suggestions

### Admin Endpoints
- `POST /api/v1/admin/ingest` - Trigger data ingestion
- `GET /api/v1/admin/status` - Get system status
- `DELETE /api/v1/admin/clear-cache` - Clear vector cache

## 🐛 Common Issues

### Database Connection
- Ensure PostgreSQL and Neo4j are running
- Check connection strings in `.env`
- Verify database permissions

### Vector Store
- Install appropriate FAISS/ChromaDB dependencies
- Check available memory for large embeddings
- Monitor disk space for vector indices

### Performance
- Use Redis caching for frequent queries
- Implement connection pooling
- Monitor API response times

## 📞 Support

For backend-specific issues:
- Check the logs: `tail -f logs/backend.log`
- Review API documentation at `/docs`
- Test endpoints with included Postman collection
