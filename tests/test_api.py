"""Tests for the FastAPI backend endpoints."""

import pytest
from unittest.mock import Mock, patch
from fastapi import status


class TestCourseStatsEndpoint:
    """Test the /api/courses endpoint."""
    
    def test_get_course_stats_success(self, client):
        """Test successful retrieval of course statistics."""
        # Mock the RAG system's get_course_analytics method
        with patch('app.rag_system.get_course_analytics') as mock_analytics:
            mock_analytics.return_value = {
                "total_courses": 2,
                "course_titles": ["Course 1", "Course 2"]
            }
            
            response = client.get("/api/courses")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_courses"] == 2
            assert data["course_titles"] == ["Course 1", "Course 2"]
            mock_analytics.assert_called_once()
    
    def test_get_course_stats_error(self, client):
        """Test error handling in course statistics endpoint."""
        with patch('app.rag_system.get_course_analytics') as mock_analytics:
            mock_analytics.side_effect = Exception("Database error")
            
            response = client.get("/api/courses")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Database error" in response.json()["detail"]


class TestQueryEndpoint:
    """Test the /api/query endpoint."""
    
    def test_query_with_session_id(self, client, sample_query_request):
        """Test query endpoint with provided session ID."""
        with patch('app.rag_system.query') as mock_query:
            mock_query.return_value = (
                "Testing is a process of evaluating software.", 
                ["source1.txt", "source2.txt"]
            )
            
            response = client.post("/api/query", json=sample_query_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["answer"] == "Testing is a process of evaluating software."
            assert data["sources"] == ["source1.txt", "source2.txt"]
            assert data["session_id"] == "test-session-123"
            mock_query.assert_called_once_with("What is testing?", "test-session-123")
    
    def test_query_without_session_id(self, client):
        """Test query endpoint without session ID (should create new session)."""
        with patch('app.rag_system.query') as mock_query, \
             patch('app.rag_system.session_manager.create_session') as mock_create_session:
            
            mock_create_session.return_value = "new-session-456"
            mock_query.return_value = (
                "Testing is important for software quality.", 
                ["source3.txt"]
            )
            
            request_data = {"query": "Why is testing important?"}
            response = client.post("/api/query", json=request_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["answer"] == "Testing is important for software quality."
            assert data["sources"] == ["source3.txt"]
            assert data["session_id"] == "new-session-456"
            
            mock_create_session.assert_called_once()
            mock_query.assert_called_once_with("Why is testing important?", "new-session-456")
    
    def test_query_with_invalid_request(self, client):
        """Test query endpoint with missing required fields."""
        response = client.post("/api/query", json={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_query_error_handling(self, client, sample_query_request):
        """Test error handling in query endpoint."""
        with patch('app.rag_system.query') as mock_query:
            mock_query.side_effect = Exception("RAG system error")
            
            response = client.post("/api/query", json=sample_query_request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "RAG system error" in response.json()["detail"]


class TestPydanticModels:
    """Test the Pydantic models used in the API."""
    
    def test_query_request_validation(self):
        """Test QueryRequest model validation."""
        from app import QueryRequest
        
        # Valid request
        valid_request = QueryRequest(query="test query", session_id="session-123")
        assert valid_request.query == "test query"
        assert valid_request.session_id == "session-123"
        
        # Request without session_id (should be None)
        minimal_request = QueryRequest(query="test query")
        assert minimal_request.query == "test query"
        assert minimal_request.session_id is None
    
    def test_query_response_creation(self):
        """Test QueryResponse model creation."""
        from app import QueryResponse
        
        response = QueryResponse(
            answer="Test answer",
            sources=["source1.txt", "source2.txt"],
            session_id="session-123"
        )
        
        assert response.answer == "Test answer"
        assert response.sources == ["source1.txt", "source2.txt"]
        assert response.session_id == "session-123"
    
    def test_course_stats_creation(self):
        """Test CourseStats model creation."""
        from app import CourseStats
        
        stats = CourseStats(
            total_courses=5,
            course_titles=["Course A", "Course B", "Course C"]
        )
        
        assert stats.total_courses == 5
        assert len(stats.course_titles) == 3
        assert "Course A" in stats.course_titles


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test endpoints using async client."""
    
    async def test_async_query_endpoint(self, async_client):
        """Test query endpoint using async client."""
        with patch('app.rag_system.query') as mock_query:
            mock_query.return_value = (
                "Async testing response", 
                ["async_source.txt"]
            )
            
            response = await async_client.post(
                "/api/query", 
                json={"query": "async test query"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "Async testing response" in data["answer"]
            assert "async_source.txt" in data["sources"]
    
    async def test_async_courses_endpoint(self, async_client):
        """Test courses endpoint using async client."""
        with patch('app.rag_system.get_course_analytics') as mock_analytics:
            mock_analytics.return_value = {
                "total_courses": 3,
                "course_titles": ["Async Course 1", "Async Course 2", "Async Course 3"]
            }
            
            response = await async_client.get("/api/courses")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_courses"] == 3
            assert len(data["course_titles"]) == 3