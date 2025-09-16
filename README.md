# Agent Builder - No-Code/Low-Code Workflow Platform

A powerful visual workflow builder that enables users to create intelligent workflows by connecting components for document processing, knowledge extraction, and AI-powered responses.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## 🌟 Live Demo

![Workflow Builder Demo](docs/demo.gif)

## 🚀 Features

- **🎨 Visual Workflow Builder**: Intuitive drag-and-drop interface for creating complex AI workflows
- **🧩 4 Core Components**: User Query, Knowledge Base, LLM Engine, and Output components
- **📄 Document Processing**: Upload and extract knowledge from PDFs with automatic text extraction
- **🔍 Vector Search**: ChromaDB integration for semantic document search and retrieval
- **🤖 Multi-LLM Support**: OpenAI GPT and Google Gemini integration with configurable parameters
- **🌐 Web Search**: SerpAPI integration for real-time web information retrieval
- **💬 Chat Interface**: Interactive chat for workflow execution and testing
- **⚡ Modern UI**: Built with React, Shadcn UI, and React Flow for optimal user experience
- **🔧 Component Configuration**: Rich configuration panels for each component type
- **💾 Workflow Persistence**: Save and load workflows with full state management
- **✅ Workflow Validation**: Built-in validation to ensure workflow correctness
- **📊 Execution Tracking**: Detailed execution logs and performance metrics

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│      Frontend       │    │       Backend       │    │      Database       │
│     (React.js)      │◄──►│     (FastAPI)       │◄──►│   (PostgreSQL)      │
│                     │    │                     │    │                     │
│ • Workflow Builder  │    │ • REST API          │    │ • Workflow Storage  │
│ • Component Library │    │ • Document Service  │    │ • Document Metadata │
│ • Chat Interface    │    │ • LLM Integration   │    │ • Chat History      │
│ • Configuration UI  │    │ • Vector Storage    │    │ • Session Data      │
│ • Real-time Updates │    │ • Workflow Engine   │    │ • User Preferences  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │
                              ┌───────┼───────┐
                              │       │       │
                          ┌───▼───┐ ┌─▼─┐ ┌───▼────┐
                          │OpenAI │ │...│ │ChromaDB│
                          │  API  │ │   │ │Vector  │
                          │       │ │   │ │  Store │
                          └───────┘ └───┘ └────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React.js 18** - Modern UI framework with hooks and TypeScript
- **Vite** - Fast build tool and development server
- **Shadcn UI** - Beautiful and accessible component library
- **React Flow** - Advanced drag-and-drop workflow builder
- **Tailwind CSS** - Utility-first CSS framework
- **TypeScript** - Type-safe JavaScript development
- **Vitest** - Fast unit test framework
- **Axios** - HTTP client for API communication
- **React Router** - Client-side routing

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Python SQL toolkit and ORM
- **PostgreSQL** - Robust relational database
- **ChromaDB** - Vector database for embeddings
- **OpenAI SDK** - Integration with OpenAI GPT models
- **Google Generative AI** - Integration with Gemini models
- **PyMuPDF** - PDF text extraction library
- **SerpAPI** - Web search API integration
- **Alembic** - Database migration tool

## 📦 Quick Start

### Option 1: Automated Setup (Recommended)

**Windows:**
```cmd
git clone <repository-url>
cd agent-builder
setup.bat
```

**Linux/MacOS:**
```bash
git clone <repository-url>
cd agent-builder
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

#### Prerequisites
- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.9 or higher) - [Download](https://www.python.org/downloads/)
- **PostgreSQL** (v12 or higher) - [Download](https://www.postgresql.org/download/)

#### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables:**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/agent_builder
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_KEY=your_serpapi_key_here
CHROMA_DB_PATH=./chroma_db
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

5. **Setup database:**
```bash
# Create database (PostgreSQL must be running)
createdb agent_builder

# Run migrations
python -m alembic upgrade head
```

6. **Start backend server:**
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Setup environment variables:**
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

4. **Start frontend server:**
```bash
npm run dev
```

### 🎉 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 How to Use

### 1. Creating Your First Workflow

1. **Access the Dashboard**: Navigate to http://localhost:3000
2. **Create New Workflow**: Click "New Workflow" button
3. **Name Your Workflow**: Give it a descriptive name and description

### 2. Building the Workflow

1. **Drag Components**: From the component library (left panel) to the canvas
2. **Connect Components**: Draw lines between component connection points
3. **Configure Components**: Click on components to access configuration panel (right)

### 3. Essential Workflow Pattern

```
User Query → Knowledge Base → LLM Engine → Output
```

**Minimum viable workflow:**
- **User Query**: Entry point for questions
- **Output**: Display responses

**Enhanced workflow with knowledge:**
- **User Query**: Entry point
- **Knowledge Base**: PDF document search
- **LLM Engine**: AI processing with context
- **Output**: Formatted responses

### 4. Component Configuration

#### User Query Component
- **Placeholder Text**: Custom input placeholder
- **Validation**: Enable input validation

#### Knowledge Base Component
- **Upload Documents**: PDF files for knowledge extraction
- **Search Limit**: Number of relevant passages to retrieve (1-20)
- **Similarity Threshold**: Minimum similarity for content matching (0.1-1.0)

#### LLM Engine Component
- **Model Selection**: Choose from GPT-3.5, GPT-4, or Gemini Pro
- **Custom Prompt**: Additional instructions for the AI
- **Temperature**: Creativity level (0.0-2.0)
- **Max Tokens**: Response length limit (100-4000)
- **Web Search**: Enable real-time web information retrieval

#### Output Component
- **Format**: Plain text, Markdown, or HTML
- **Show Sources**: Display document sources in responses
- **Execution Time**: Show workflow performance metrics

### 5. Testing Your Workflow

1. **Validate**: Click "Validate" to check workflow structure
2. **Build Stack**: Click "Build Stack" to prepare for execution
3. **Chat Interface**: Test with real queries in the chat modal

## 🔧 Advanced Configuration

### Environment Variables

#### Backend Configuration (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/agent_builder

# AI Services
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-ai-key
SERPAPI_KEY=your-serpapi-key

# Storage
CHROMA_DB_PATH=./chroma_db

# Security
SECRET_KEY=your-secure-secret-key

# Environment
ENVIRONMENT=development
```

#### Frontend Configuration (.env.local)
```env
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

### API Endpoints

#### Core Endpoints
- `GET /` - API health check
- `GET /health` - Detailed system health
- `GET /docs` - Interactive API documentation (Swagger UI)

#### Workflow Management
- `POST /api/workflows/` - Create new workflow
- `GET /api/workflows/` - List all workflows
- `GET /api/workflows/{id}` - Get specific workflow
- `PUT /api/workflows/{id}` - Update workflow
- `DELETE /api/workflows/{id}` - Delete workflow
- `POST /api/workflows/{id}/validate` - Validate workflow configuration

#### Document Management
- `POST /api/documents/upload` - Upload PDF document
- `GET /api/documents/` - List all documents
- `GET /api/documents/{id}` - Get specific document
- `DELETE /api/documents/{id}` - Delete document
- `POST /api/documents/{id}/reprocess` - Reprocess embeddings

#### Chat & Execution
- `POST /api/chat/sessions` - Create chat session
- `GET /api/chat/sessions` - List chat sessions
- `POST /api/chat/execute` - Execute workflow with query
- `GET /api/chat/sessions/{id}/messages` - Get session messages

#### Component Information
- `GET /api/components/types` - Available component types
- `GET /api/components/categories` - Component categories
- `POST /api/components/validate-config` - Validate component config

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests  
```bash
# Start both backend and frontend
cd backend && uvicorn app.main:app --reload &
cd frontend && npm run dev &

# Run end-to-end tests
npm run test:e2e
```

## 🚀 Production Deployment

### Backend Deployment

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set production environment variables:**
```bash
export ENVIRONMENT=production
export DATABASE_URL=your_production_db_url
```

3. **Run migrations:**
```bash
python -m alembic upgrade head
```

4. **Start production server:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment

1. **Build production assets:**
```bash
npm run build
```

2. **Serve with nginx or similar:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/build;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Deployment (Future Enhancement)

```dockerfile
# Dockerfile example for future implementation
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **Backend fails to start**
```bash
# Check Python version
python --version  # Should be 3.9+

# Check virtual environment
which python  # Should point to venv

# Check database connection
psql -h localhost -U username -d agent_builder
```

#### 2. **Frontend fails to start**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 3. **Database connection errors**
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Check database exists
psql -l | grep agent_builder

# Verify connection string
echo $DATABASE_URL
```

#### 4. **API key errors**
```bash
# Verify environment variables are loaded
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# Check .env file location
ls -la backend/.env
```

#### 5. **CORS errors**
- Ensure frontend URL is in backend CORS origins
- Check that API_URL in frontend .env.local is correct
- Verify both servers are running on expected ports

### Debug Mode

Enable debug logging in backend:
```python
# In app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

Enable debug mode in frontend:
```bash
export REACT_APP_DEBUG=true
npm start
```

## 🚀 Deployment

### Quick Deploy to Digital Ocean

Deploy Agent Builder to Digital Ocean with our automated deployment pipeline:

#### Prerequisites
- Digital Ocean account with a Droplet (Ubuntu 20.04/22.04)
- Domain name (recommended for SSL)
- API keys (OpenAI, Google AI, SerpAPI)

#### 1. Automated Setup
```bash
# On your Digital Ocean droplet
wget https://raw.githubusercontent.com/dhruvp66572/Agent_builder/main/deploy/setup-digitalocean.sh
chmod +x setup-digitalocean.sh
sudo ./setup-digitalocean.sh
```

#### 2. Configure Environment
```bash
cd /opt/agent-builder
sudo nano .env  # Add your API keys and configuration
```

#### 3. Deploy
```bash
sudo docker-compose up -d
```

### GitHub Actions CI/CD

Automatic deployment with GitHub Actions:

1. **Fork this repository**
2. **Configure secrets** in GitHub repository settings:
   - `DOCKER_USERNAME` - Docker Hub username
   - `DOCKER_PASSWORD` - Docker Hub access token
   - `DIGITALOCEAN_ACCESS_TOKEN` - DO API token
   - `DIGITALOCEAN_SSH_PRIVATE_KEY` - SSH private key
   - `DIGITALOCEAN_SERVER_IP` - Your droplet IP

3. **Push to main branch** - Automatic deployment triggers!

### Docker Deployment

Local Docker deployment:

```bash
# Production
docker-compose up -d

# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

📖 **Full Deployment Guide**: [deploy/DEPLOYMENT.md](deploy/DEPLOYMENT.md)
🔐 **Secrets Setup Guide**: [deploy/SECRETS.md](deploy/SECRETS.md)

## 📚 Additional Resources

- [Development Guide](DEVELOPMENT.md) - Detailed development information
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Deployment Guide](deploy/DEPLOYMENT.md) - Production deployment guide
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass: `npm test` and `pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Style
- **Frontend**: ESLint + Prettier
- **Backend**: Black + isort
- **Documentation**: Markdown with consistent formatting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support & Community

- **Issues**: [GitHub Issues](https://github.com/your-repo/agent-builder/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/agent-builder/discussions)
- **Documentation**: [Wiki](https://github.com/your-repo/agent-builder/wiki)
- **Email**: support@agent-builder.com

## 🎖️ Acknowledgments

- **OpenAI** for GPT models and embeddings
- **Google** for Gemini AI integration
- **React Flow** for the amazing workflow builder component
- **Shadcn/ui** for the beautiful UI components
- **FastAPI** for the excellent Python web framework
- **ChromaDB** for vector storage capabilities

---

**Built with ❤️ by the Agent Builder Team**