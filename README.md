# GeoVerse 🌍

An advanced AI-powered question-answering system for geospatial and earth observation data, specifically designed to interact with the MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre) portal.

## 🎯 Project Overview

GeoVerse is a sophisticated Retrieval-Augmented Generation (RAG) system that intelligently processes and queries diverse content types from the MOSDAC portal, including static web pages, PDFs, dynamic JavaScript-rendered content, and multimodal atlas documents.

### Key Features

- **Multi-source Data Ingestion**: Processes static HTML, PDFs, DOCX files, and dynamic web content
- **Knowledge Graph Integration**: Models relationships between satellites, missions, and data products
- **Multimodal Processing**: Handles both textual and visual content from atlas PDFs
- **Hybrid Retrieval**: Combines vector similarity search with knowledge graph querying
- **Conversational Interface**: Natural language question-answering with citation support

## 🚀 Development Phases

### Phase 1: Foundational Content Retrieval (MVP) ✅
- Basic web scraping of static HTML pages
- PDF and DOCX text extraction
- Core RAG pipeline with vector embeddings
- FastAPI backend with basic endpoints

### Phase 2: Adding Structure and Intelligence 🔄
- Knowledge graph creation with Neo4j
- Named Entity Recognition (NER) for domain entities
- Hybrid retrieval combining KG and vector search
- Enhanced query understanding

### Phase 3: Handling Advanced & Dynamic Content 📋
- JavaScript-rendered page processing
- Multimodal atlas PDF handling with OCR
- Visual content embedding and retrieval
- Image-based query responses

### Phase 4: Productionizing and User Experience 📋
- Production-grade React frontend
- FastAPI backend optimization
- Docker containerization
- Advanced UI features (conversation history, map interface)

## 🛠️ Technology Stack

### Data Processing & Retrieval
- **Web Scraping**: Scrapy, BeautifulSoup, Selenium/Playwright
- **Document Processing**: PyMuPDF, python-docx, Tesseract OCR
- **Vector Database**: FAISS or ChromaDB
- **Knowledge Graph**: Neo4j
- **Embeddings**: Sentence-Transformers, CLIP (multimodal)

### AI & ML
- **Framework**: LangChain
- **NLP**: spaCy for Named Entity Recognition
- **LLM Integration**: OpenAI API, Hugging Face Transformers

### Backend & API
- **API Framework**: FastAPI
- **Database**: PostgreSQL (metadata), Neo4j (knowledge graph)
- **Task Queue**: Celery with Redis

### Frontend & UI
- **Framework**: React.js
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit
- **HTTP Client**: Axios

### DevOps & Deployment
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes (optional)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana

## 📁 Project Structure

```
GeoVerse/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── backend/               # Backend services and APIs
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── ingestion/           # Phase 1: Data ingestion pipeline
│   │   │   ├── __init__.py
│   │   │   ├── web_scraper.py
│   │   │   ├── pdf_processor.py
│   │   │   ├── docx_processor.py
│   │   │   └── sitemap_parser.py
│   │   │
│   │   ├── knowledge_graph/     # Phase 2: KG creation and management
│   │   │   ├── __init__.py
│   │   │   ├── entity_extractor.py
│   │   │   ├── graph_builder.py
│   │   │   └── graph_queries.py
│   │   │
│   │   ├── retrieval/          # Core RAG functionality
│   │   │   ├── __init__.py
│   │   │   ├── embeddings.py
│   │   │   ├── vector_store.py
│   │   │   ├── hybrid_retriever.py
│   │   │   └── reranker.py
│   │   │
│   │   ├── multimodal/         # Phase 3: Advanced content processing
│   │   │   ├── __init__.py
│   │   │   ├── js_renderer.py
│   │   │   ├── atlas_processor.py
│   │   │   ├── ocr_engine.py
│   │   │   └── multimodal_embeddings.py
│   │   │
│   │   ├── api/               # FastAPI backend
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── search.py
│   │   │   │   └── admin.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── request_models.py
│   │   │   │   └── response_models.py
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       └── rate_limiting.py
│   │   │
│   │   ├── llm/               # LLM integration and prompt management
│   │   │   ├── __init__.py
│   │   │   ├── chat_engine.py
│   │   │   ├── prompt_templates.py
│   │   │   └── response_generator.py
│   │   │
│   │   └── utils/             # Shared utilities
│   │       ├── __init__.py
│   │       ├── config.py
│   │       ├── logging.py
│   │       ├── database.py
│   │       └── text_processing.py
│   │
│   ├── tests/                # Backend tests
│   │   ├── __init__.py
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   ├── scripts/              # Backend utility scripts
│   │   ├── setup_database.py
│   │   ├── run_ingestion.py
│   │   └── backup_data.py
│   │
│   └── config/               # Backend configuration
│       ├── development.yml
│       ├── production.yml
│       ├── neo4j.conf
│       └── logging.conf
│
├── frontend/              # React Frontend Application
│   ├── README.md
│   ├── package.json
│   ├── package-lock.json
│   ├── Dockerfile
│   ├── .env.example
│   ├── .gitignore
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInterface.jsx
│   │   │   │   ├── MessageList.jsx
│   │   │   │   └── InputBox.jsx
│   │   │   ├── Search/
│   │   │   │   ├── SearchBar.jsx
│   │   │   │   ├── SearchResults.jsx
│   │   │   │   └── Filters.jsx
│   │   │   ├── Layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Footer.jsx
│   │   │   └── Common/
│   │   │       ├── LoadingSpinner.jsx
│   │   │       ├── ErrorBoundary.jsx
│   │   │       └── Modal.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Chat.jsx
│   │   │   ├── Search.jsx
│   │   │   └── About.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── websocket.js
│   │   │   └── storage.js
│   │   ├── hooks/
│   │   │   ├── useChat.js
│   │   │   ├── useSearch.js
│   │   │   └── useAuth.js
│   │   ├── store/
│   │   │   ├── index.js
│   │   │   ├── slices/
│   │   │   │   ├── chatSlice.js
│   │   │   │   ├── searchSlice.js
│   │   │   │   └── uiSlice.js
│   │   ├── utils/
│   │   │   ├── constants.js
│   │   │   ├── helpers.js
│   │   │   └── formatters.js
│   │   └── styles/
│   │       ├── globals.css
│   │       ├── components.css
│   │       └── tailwind.css
│   ├── build/
│   └── tests/
│       ├── components/
│       ├── pages/
│       └── utils/
│
├── shared/                # Shared resources and documentation
│   ├── docs/              # Project documentation
│   │   ├── api_reference.md
│   │   ├── deployment_guide.md
│   │   ├── architecture.md
│   │   ├── backend_setup.md
│   │   ├── frontend_setup.md
│   │   └── collaboration_guide.md
│   │
│   ├── data/              # Shared data storage
│   │   ├── raw/          # Raw scraped content
│   │   ├── processed/    # Cleaned and processed data
│   │   ├── embeddings/   # Vector embeddings
│   │   └── knowledge_graph/  # Neo4j exports
│   │
│   └── config/           # Shared configuration
│       ├── docker/
│       └── deployment/
│
├── notebooks/            # Jupyter notebooks for experiments
│   ├── data_exploration.ipynb
│   ├── model_evaluation.ipynb
│   └── prototype_testing.ipynb
│
└── scripts/              # Project-wide utility scripts
    ├── setup_project.py
    ├── deploy.sh
    └── dev_setup.sh

```

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+ (for frontend development)
- Docker & Docker Compose
- Neo4j database
- Redis (for task queue)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/GeoVerse.git
   cd GeoVerse
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment configuration**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Frontend  
   cp frontend/.env.example frontend/.env
   # Edit .env files with your configuration
   ```

5. **Start services with Docker**
   ```bash
   docker-compose up -d
   ```

### Development Setup

**Backend (FastAPI)**
```bash
cd backend
uvicorn src.api.main:app --reload --port 8000
```

**Frontend (React)**
```bash
cd frontend
npm start
```

### Quick Start (Phase 1)

```bash
# Backend - Start FastAPI server
cd backend
uvicorn src.api.main:app --reload --port 8000

# In another terminal - Frontend
cd frontend  
npm start

# Backend - Run data ingestion
cd backend
python scripts/run_ingestion.py --phase 1 --source sitemap
python scripts/run_ingestion.py --phase 1 --source web
python scripts/run_ingestion.py --phase 1 --source documents
python scripts/run_ingestion.py --phase 1 --source embeddings
```

## 📊 Current Status

- [x] Project structure setup
- [x] Basic documentation  
- [x] Docker Compose configuration
- [x] Backend FastAPI foundation
- [x] Frontend React foundation
- [x] Environment configuration templates
- [ ] Phase 1: MVP implementation
- [ ] Phase 2: Knowledge graph integration
- [ ] Phase 3: Advanced content processing
- [ ] Phase 4: Production deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre)
- Indian Space Research Organisation (ISRO)
- Open source community for the amazing tools and libraries

## 📞 Contact

- **Project Lead**: [Your Name]
- **Email**: [your.email@example.com]
- **GitHub**: [@yourusername](https://github.com/yourusername)

---

**Built with ❤️ for advancing geospatial data accessibility through AI**
