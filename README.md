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
- ✅ Comprehensive MOSDAC portal scraping (69+ documents)
- ✅ Vector embeddings with FAISS index
- ✅ OpenRouter Gemini 2.5 Pro integration
- ✅ Production-ready FastAPI backend
- ✅ Context-aware RAG pipeline with source attribution

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
- **Web Scraping**: BeautifulSoup, Requests
- **Vector Database**: FAISS
- **Embeddings**: Sentence-Transformers
- **Content Processing**: Intelligent text extraction and categorization
- **Document Processing**: PyMuPDF, python-docx, Tesseract OCR (Phase 3)

### AI & ML
- **LLM**: OpenRouter Gemini 2.5 Pro
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Vector Database**: FAISS
- **Framework**: Custom RAG pipeline
- **NLP**: spaCy for Named Entity Recognition (Phase 2)

### Backend & API
- **API Framework**: FastAPI
- **LLM Integration**: OpenRouter API
- **Vector Search**: FAISS with cosine similarity
- **Database**: PostgreSQL (metadata), Neo4j (knowledge graph - Phase 2)
- **Task Queue**: Celery with Redis (Phase 4)

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
├── backend/               # 🚀 Production-Ready Backend
│   ├── start_production.py     # Single command server start
│   ├── scraper.py             # Comprehensive data collection
│   ├── production_demo.py     # System testing & validation
│   ├── setup_data.py          # Data utilities
│   ├── requirements.txt       # Minimal dependencies
│   ├── .env                   # Configuration (OpenRouter)
│   ├── README.md              # Backend documentation
│   ├── Dockerfile
│   │
│   ├── src/                   # Core application code
│   │   ├── api/              # FastAPI routes and models
│   │   ├── llm/              # OpenRouter Gemini integration
│   │   ├── retrieval/        # Vector search and embeddings
│   │   ├── ingestion/        # Data processing pipeline
│   │   └── utils/            # Configuration and utilities
│   │
│   ├── data/embeddings/      # Vector database (69+ documents)
│   └── logs/                 # Application logs
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

## � Quick Start (Production Ready!)

The backend is fully functional and production-ready. Here's how to get started:

### **Option 1: Use Existing System (Recommended)**
```bash
cd backend
python start_production.py
```
✅ **Ready to use!** The system already has 69+ documents indexed.

### **Option 2: Fresh Setup**
```bash
cd backend
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (add your OpenRouter API key)
# Edit .env file: OPENROUTER_API_KEY=your_key_here

# 3. Create knowledge base
python scraper.py

# 4. Start server
python start_production.py
```

### **Test the System**
```bash
# In another terminal
cd backend
python production_demo.py
```

### **API Usage**
- **Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Chat Endpoint**: POST `/api/v1/chat`

Example:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is MOSDAC?"}'
```

## �🚦 Getting Started

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

### Development Setup (Advanced)

For development and extending the system:

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
# Backend - Start production server
cd backend
python start_production.py

# In another terminal - Frontend (Phase 4)
cd frontend  
npm start

# Backend - Run data ingestion (First time setup)
cd backend
python scraper.py
```

## 📊 Current Status

- [x] **Phase 1: MVP Complete** ✅
  - [x] Comprehensive MOSDAC data ingestion (69+ documents)
  - [x] Production-ready FastAPI backend
  - [x] OpenRouter Gemini 2.5 Pro integration
  - [x] Vector search with FAISS
  - [x] Context-aware response generation
  - [x] Single-command deployment
- [x] Project structure setup ✅
- [x] Backend optimization and cleanup ✅
- [x] Production documentation ✅
- [ ] Frontend React application (Phase 4)
- [ ] Phase 2: Knowledge graph integration
- [ ] Phase 3: Advanced content processing
- [ ] Phase 4: Production deployment with UI

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

---

## 🌐 Deployment Guide

### Backend (FastAPI) on Render
1. **Connect your repo to Render**
2. **Create a new Web Service**
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python start_production.py`
   - Python Version: 3.10 or 3.11
3. **Set Environment Variables** (in Render dashboard):
   - `ENVIRONMENT=production`
   - `LOG_LEVEL=INFO`
   - `ALLOWED_ORIGINS=https://your-vercel-app.vercel.app`
   - `FRONTEND_URL=https://your-vercel-app.vercel.app`
   - Any LLM API keys (e.g. `GEMINI_API_KEY`, `OPENROUTER_API_KEY`)
   - Any custom config (see `backend/src/utils/config.py`)
4. **Data Folder**
   - Place your data in `backend/data` (or use Render persistent disk)
5. **Deploy**
   - Note your Render service’s public URL (e.g. `https://geoverse-backend.onrender.com`)

### Frontend (Next.js) on Vercel
1. **Connect your repo to Vercel**
2. **Create a new Project**
   - Select the `frontend` directory
3. **Set Environment Variables** (in Vercel Project Settings):
   - `NEXT_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com`
4. **Deploy**
   - Your app will be live at `https://your-vercel-app.vercel.app`

## 🛠️ Environment Variables Example

### Backend `.env.example`
```
ENVIRONMENT=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
FRONTEND_URL=https://your-vercel-app.vercel.app
GEMINI_API_KEY=your_gemini_key
OPENROUTER_API_KEY=your_openrouter_key
# Add any other required keys from config.py
```

### Frontend `.env.example`
```
NEXT_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com
```

## 🧩 Troubleshooting
- **CORS errors:** Ensure `ALLOWED_ORIGINS` and `FRONTEND_URL` match your Vercel URL in Render backend settings.
- **Data not found:** Make sure your data is present in `backend/data` and is included in your repo or persistent disk.
- **API errors:** Check logs in Render dashboard for details.
- **Chatbot response cut off:** Increase `fallback_context_chars` and `max_tokens` in backend config or environment.

---
For more help, see comments in `backend/src/utils/config.py` and `backend/README.md`.
