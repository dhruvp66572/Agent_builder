# Development Scripts

## Start Development Environment

### Option 1: Manual Setup

1. **Backend Server:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Frontend Server:**
```bash
cd frontend
npm start
```

### Option 2: Using Docker (Future Enhancement)

```bash
docker-compose up -dev
```

## API Endpoints

### Core Endpoints
- `GET /` - API health check
- `GET /health` - System health status
- `GET /docs` - Interactive API documentation

### Document Management
- `POST /api/documents/upload` - Upload PDF document
- `GET /api/documents/` - List all documents
- `GET /api/documents/{id}` - Get specific document
- `DELETE /api/documents/{id}` - Delete document
- `POST /api/documents/{id}/reprocess` - Reprocess document embeddings

### Workflow Management
- `POST /api/workflows/` - Create new workflow
- `GET /api/workflows/` - List all workflows
- `GET /api/workflows/{id}` - Get specific workflow
- `PUT /api/workflows/{id}` - Update workflow
- `DELETE /api/workflows/{id}` - Delete workflow
- `POST /api/workflows/{id}/validate` - Validate workflow

### Chat & Execution
- `POST /api/chat/sessions` - Create chat session
- `GET /api/chat/sessions` - List chat sessions
- `POST /api/chat/execute` - Execute workflow with query
- `GET /api/chat/sessions/{id}/messages` - Get session messages

### Component Information
- `GET /api/components/types` - Get available component types
- `GET /api/components/categories` - Get component categories
- `POST /api/components/validate-config` - Validate component configuration

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/agent_builder
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
SERPAPI_KEY=your_serpapi_key
CHROMA_DB_PATH=./chroma_db
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

### Frontend (.env.local)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## Database Setup

### PostgreSQL Installation
1. Install PostgreSQL from https://www.postgresql.org/download/
2. Create database: `createdb agent_builder`
3. Update DATABASE_URL in backend/.env

### Run Migrations
```bash
cd backend
python -m alembic upgrade head
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Production Deployment

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
# Serve build folder with nginx or similar
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Backend: Change port with `--port 8001`
   - Frontend: Set PORT=3001 in .env.local

2. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in .env
   - Verify database exists

3. **Missing API Keys**
   - Update .env with valid API keys
   - Restart backend server after changes

4. **CORS Issues**
   - Ensure frontend URL is in CORS origins
   - Check API_URL in frontend .env.local

5. **Package Installation Issues**
   - Backend: Use virtual environment
   - Frontend: Clear node_modules and reinstall

### Logs
- Backend logs: Console output from uvicorn
- Frontend logs: Browser developer console
- Database logs: PostgreSQL logs directory