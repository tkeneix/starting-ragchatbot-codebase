"""Pytest configuration and shared fixtures for testing."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
import tempfile
import shutil
from pathlib import Path

# Add the backend directory to the Python path
import sys
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app import app
from config import Config
from rag_system import RAGSystem


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def temp_docs_dir():
    """Create a temporary directory with sample course documents."""
    temp_dir = tempfile.mkdtemp()
    
    # Create a sample course document
    sample_doc = """Course Title: Sample Course
Course Link: https://example.com/course
Course Instructor: Test Instructor

Lesson 1: Introduction to Testing
Lesson Link: https://example.com/lesson1
This is the content of lesson 1. It explains basic testing concepts.

Lesson 2: Advanced Testing
Lesson Link: https://example.com/lesson2
This is the content of lesson 2. It covers advanced testing techniques.
"""
    
    with open(os.path.join(temp_dir, "sample_course.txt"), "w") as f:
        f.write(sample_doc)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config():
    """Create a test configuration."""
    return Config(
        anthropic_api_key="test-key",
        chunk_size=500,
        chunk_overlap=50,
        max_search_results=3,
        max_conversation_history=2
    )


@pytest.fixture
def sample_query_request():
    """Sample query request data."""
    return {
        "query": "What is testing?",
        "session_id": "test-session-123"
    }