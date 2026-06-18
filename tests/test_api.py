"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.main import app
from app.models.schemas import (
    ExpertResponse,
    ContributorResponse,
    AnalysisResponse,
    ExpertProfile,
    ContributorProfile,
    UserProfile,
    MessageSummary
)

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "Bobager API"


def test_health_endpoint():
    """Test health check endpoint."""
    with patch("app.api.routes.slack_mcp_client.health_check", new_callable=AsyncMock) as mock_slack, \
         patch("app.api.routes.bob_client.health_check", new_callable=AsyncMock) as mock_bob:
        
        mock_slack.return_value = True
        mock_bob.return_value = True
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["slack_mcp_connected"] is True
        assert data["bob_api_connected"] is True


def test_find_experts_get():
    """Test GET endpoint for finding experts."""
    mock_response = ExpertResponse(
        topic="Python",
        experts=[
            ExpertProfile(
                user=UserProfile(
                    user_id="U123",
                    username="john_doe",
                    real_name="John Doe"
                ),
                expertise_score=0.85,
                message_count=25,
                relevant_messages=[],
                key_topics=["Python", "FastAPI", "async"],
                analysis="Expert in Python development"
            )
        ],
        total_found=1,
        timeframe_days=30,
        analysis_timestamp=datetime.now()
    )
    
    with patch("app.api.routes.analysis_service.find_experts", new_callable=AsyncMock) as mock_find:
        mock_find.return_value = mock_response
        
        response = client.get("/api/v1/experts/Python?timeframe_days=30&min_messages=5")
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "Python"
        assert len(data["experts"]) == 1
        assert data["experts"][0]["expertise_score"] == 0.85


def test_find_experts_post():
    """Test POST endpoint for finding experts."""
    mock_response = ExpertResponse(
        topic="React",
        experts=[],
        total_found=0,
        timeframe_days=30,
        analysis_timestamp=datetime.now()
    )
    
    with patch("app.api.routes.analysis_service.find_experts", new_callable=AsyncMock) as mock_find:
        mock_find.return_value = mock_response
        
        response = client.post(
            "/api/v1/experts",
            json={
                "topic": "React",
                "timeframe_days": 30,
                "min_messages": 5,
                "channels": ["frontend"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "React"
        assert data["total_found"] == 0


def test_find_contributors_get():
    """Test GET endpoint for finding contributors."""
    mock_response = ContributorResponse(
        channel="engineering",
        contributors=[
            ContributorProfile(
                user=UserProfile(
                    user_id="U456",
                    username="jane_smith",
                    real_name="Jane Smith"
                ),
                message_count=50,
                engagement_score=0.92,
                top_threads=[],
                contribution_summary="Active contributor"
            )
        ],
        total_found=1,
        timeframe_days=30,
        analysis_timestamp=datetime.now()
    )
    
    with patch("app.api.routes.analysis_service.find_contributors", new_callable=AsyncMock) as mock_find:
        mock_find.return_value = mock_response
        
        response = client.get("/api/v1/contributors/engineering?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "engineering"
        assert len(data["contributors"]) == 1
        assert data["contributors"][0]["engagement_score"] == 0.92


def test_custom_analysis():
    """Test custom analysis endpoint."""
    mock_response = AnalysisResponse(
        query="Who are the DevOps experts?",
        insights="Found 3 DevOps experts based on their contributions",
        relevant_users=[],
        relevant_messages=[],
        metadata={"total_messages_analyzed": 100},
        analysis_timestamp=datetime.now()
    )
    
    with patch("app.api.routes.analysis_service.custom_analysis", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_response
        
        response = client.post(
            "/api/v1/analyze",
            json={
                "query": "Who are the DevOps experts?",
                "timeframe_days": 60
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Who are the DevOps experts?"
        assert "insights" in data


def test_cache_stats():
    """Test cache stats endpoint."""
    response = client.get("/api/v1/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "cache_stats" in data
    assert "timestamp" in data


def test_clear_cache():
    """Test clear cache endpoint."""
    response = client.post("/api/v1/cache/clear")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Cache cleared successfully"


def test_invalid_topic():
    """Test error handling for invalid requests."""
    with patch("app.api.routes.analysis_service.find_experts", new_callable=AsyncMock) as mock_find:
        mock_find.side_effect = Exception("Invalid topic")
        
        response = client.get("/api/v1/experts/InvalidTopic")
        assert response.status_code == 500


def test_validation_error():
    """Test validation error handling."""
    response = client.post(
        "/api/v1/experts",
        json={
            "topic": "Python",
            "timeframe_days": 500,  # Exceeds maximum
            "min_messages": 5
        }
    )
    assert response.status_code == 422  # Validation error

# Made with Bob
