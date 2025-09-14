import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.main import app
from app.database import get_db, Base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestAPI:
    def test_health_check(self):
        """Test API health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Agent Builder API is running" in response.json()["message"]

    def test_create_workflow(self):
        """Test workflow creation"""
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow",
            "workflow_data": {
                "nodes": [],
                "edges": []
            }
        }
        response = client.post("/api/workflows/", json=workflow_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Test Workflow"

    def test_list_workflows(self):
        """Test listing workflows"""
        response = client.get("/api/workflows/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_component_types(self):
        """Test getting component types"""
        response = client.get("/api/components/types")
        assert response.status_code == 200
        data = response.json()
        assert "user-query" in data
        assert "knowledge-base" in data
        assert "llm-engine" in data
        assert "output" in data

    def test_validate_workflow_config(self):
        """Test workflow validation"""
        # Create a workflow first
        workflow_data = {
            "name": "Validation Test",
            "description": "Test validation",
            "workflow_data": {
                "nodes": [
                    {
                        "id": "1",
                        "type": "user-query",
                        "data": {"config": {}}
                    },
                    {
                        "id": "2", 
                        "type": "output",
                        "data": {"config": {}}
                    }
                ],
                "edges": [
                    {
                        "id": "e1-2",
                        "source": "1",
                        "target": "2"
                    }
                ]
            }
        }
        
        create_response = client.post("/api/workflows/", json=workflow_data)
        workflow_id = create_response.json()["id"]
        
        # Validate the workflow
        response = client.post(f"/api/workflows/{workflow_id}/validate")
        assert response.status_code == 200
        assert response.json()["valid"] == True

    def test_create_chat_session(self):
        """Test chat session creation"""
        # Create workflow first
        workflow_data = {
            "name": "Chat Test",
            "workflow_data": {"nodes": [], "edges": []}
        }
        workflow_response = client.post("/api/workflows/", json=workflow_data)
        workflow_id = workflow_response.json()["id"]
        
        # Create chat session
        session_data = {
            "workflow_id": workflow_id,
            "session_name": "Test Session"
        }
        response = client.post("/api/chat/sessions", json=session_data)
        assert response.status_code == 200
        assert response.json()["workflow_id"] == workflow_id

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
    
    # Clean up test database
    if os.path.exists("./test.db"):
        os.remove("./test.db")