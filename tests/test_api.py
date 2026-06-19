"""Tests for API endpoints."""
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.main import app
from chat_with_slack import format_results, parse_user_query
from app.services.analysis_service import analysis_service
from app.services.slack_service import slack_service
from app.utils.cache import cache_manager
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


@pytest.mark.asyncio
async def test_custom_analysis_handles_dict_references():
    """Custom analysis tolerates dict-shaped user and message references from Ollama."""
    messages = [
        {
            "ts": "123.456",
            "user": "U123",
            "channel": "general",
            "text": "Pizza Friday is back"
        }
    ]
    user_profiles = {
        "U123": {
            "id": "U123",
            "name": "david",
            "real_name": "David"
        }
    }

    with patch.object(analysis_service.slack_service, "get_messages_by_topic", new=AsyncMock(return_value=messages)), \
         patch.object(analysis_service.slack_service, "get_user_profiles", new=AsyncMock(return_value=user_profiles)), \
         patch.object(
             analysis_service.ollama_client,
             "custom_analysis",
             new=AsyncMock(
                 return_value={
                     "insights": {"summary": "David mentions pizza the most."},
                     "relevant_users": [{"user_id": "U123"}],
                     "key_messages": [{"ts": "123.456"}]
                 }
             )
         ):
        result = await analysis_service.custom_analysis("Who talks about pizza the most?")

    assert result.relevant_users[0].user_id == "U123"
    assert result.relevant_messages[0].message_id == "123.456"
    assert "summary" in result.insights


@pytest.mark.asyncio
async def test_custom_analysis_sanitizes_unknown_user_ids():
    """Insights should not leak fabricated Slack IDs from model output."""
    messages = [
        {
            "ts": "123.456",
            "user": "U123",
            "channel": "general",
            "text": "DevOps automation is improving deployments"
        }
    ]
    user_profiles = {
        "U123": {
            "id": "U123",
            "name": "david",
            "real_name": "David"
        }
    }

    with patch.object(analysis_service.slack_service, "get_messages_by_topic", new=AsyncMock(return_value=messages)), \
         patch.object(analysis_service.slack_service, "get_user_profiles", new=AsyncMock(return_value=user_profiles)), \
         patch.object(
             analysis_service.ollama_client,
             "custom_analysis",
             new=AsyncMock(
                 return_value={
                     "insights": "U123 and U456 mentioned devops the most.",
                     "relevant_users": ["U123", "U456"],
                     "key_messages": []
                 }
             )
         ):
        result = await analysis_service.custom_analysis("Who mentions devops the most?")

    assert "David" in result.insights
    assert "U456" not in result.insights
    assert [user.user_id for user in result.relevant_users] == ["U123"]


@pytest.mark.asyncio
async def test_format_results_uses_validated_custom_analysis_fields():
    """Chat formatting for custom analysis should not invoke the LLM a second time."""
    response = AnalysisResponse(
        query="Who mentions devops the most?",
        insights="David mentions devops the most.",
        relevant_users=[
            UserProfile(
                user_id="U123",
                username="david",
                real_name="David"
            )
        ],
        relevant_messages=[],
        metadata={
            "total_messages_analyzed": 1,
            "channels_searched": "all",
            "timeframe_days": 30
        },
        analysis_timestamp=datetime.now()
    )

    formatted = await format_results("custom_analysis", response, response.query)

    assert "David mentions devops the most." in formatted
    assert "Relevant people: David (@david)." in formatted


@pytest.mark.asyncio
async def test_parse_user_query_preserves_explanation_intent():
    """Explanation-style custom analysis should keep the full user query."""
    mock_response = json.dumps({
        "tool": "custom_analysis",
        "params": {"query": "Anna Bob's code"}
    })

    with patch("chat_with_slack.call_ollama", new=AsyncMock(return_value=mock_response)):
        result = await parse_user_query("hi i am a new intern and i need help understanding the code Anna Bob wrote")

    assert result == {
        "tool": "custom_analysis",
        "params": {
            "query": "hi i am a new intern and i need help understanding the code Anna Bob wrote"
        },
    }


@pytest.mark.asyncio
async def test_format_results_skips_people_section_for_explanation_queries():
    """Explanation-style custom analysis output should not add a people section."""
    response = AnalysisResponse(
        query="help me understand the code Anna Bob wrote",
        insights="Anna Bob shared HTML for a simple Snake game UI.",
        relevant_users=[
            UserProfile(
                user_id="U123",
                username="david",
                real_name="David"
            )
        ],
        relevant_messages=[],
        metadata={
            "total_messages_analyzed": 1,
            "channels_searched": "all",
            "timeframe_days": 30
        },
        analysis_timestamp=datetime.now()
    )

    formatted = await format_results("custom_analysis", response, response.query)

    assert "Anna Bob shared HTML for a simple Snake game UI." in formatted
    assert "Relevant people:" not in formatted


@pytest.mark.asyncio
async def test_custom_analysis_uses_fallback_search_terms_for_code_questions():
    """Explanation-style code questions should retry Slack search with narrower terms."""
    cache_manager.clear()
    messages = [
        {
            "ts": "123.456",
            "user": "U123",
            "channel": "frontend",
            "text": "<!doctype html><html><body>Snake Game</body></html>",
        }
    ]
    user_profiles = {
        "U123": {
            "id": "U123",
            "name": "anna.bob",
            "real_name": "Anna Bob",
        }
    }

    async def fake_get_messages_by_topic(topic, timeframe_days=30, channels=None):
        if topic == '"Anna Bob" code':
            return messages
        return []

    with patch.object(
        analysis_service.slack_service,
        "get_messages_by_topic",
        new=AsyncMock(side_effect=fake_get_messages_by_topic),
    ) as mock_get_messages, \
         patch.object(analysis_service.slack_service, "get_user_profiles", new=AsyncMock(return_value=user_profiles)), \
         patch.object(
             analysis_service.ollama_client,
             "custom_analysis",
             new=AsyncMock(
                 return_value={
                     "insights": "Anna Bob shared HTML for a simple Snake game page.",
                     "relevant_users": [],
                     "key_messages": []
                 }
             ),
         ):
        result = await analysis_service.custom_analysis(
            "What is the code Anna Bob posted in Slack?"
        )

    searched_terms = [call.kwargs["topic"] for call in mock_get_messages.await_args_list]
    assert 'What is the code Anna Bob posted in Slack?' in searched_terms
    assert '"Anna Bob" code' in searched_terms
    assert result.insights == "Anna Bob shared HTML for a simple Snake game page."


def test_build_custom_analysis_search_terms_for_person_topic_query():
    """Person-topic questions should include author-focused Slack search terms."""
    terms = analysis_service._build_custom_analysis_search_terms(
        "What does Anna Bob talk about?"
    )

    assert "What does Anna Bob talk about?" in terms
    assert 'from:"Anna Bob"' in terms
    assert "Anna Bob" in terms


@pytest.mark.asyncio
async def test_custom_analysis_search_aggregates_across_terms():
    """Custom analysis should continue searching fallback terms after an initial hit."""
    cache_manager.clear()
    first_messages = [
        {
            "ts": "111.111",
            "user": "U999",
            "channel": "general",
            "text": "Thanks Anna Bob!",
        }
    ]
    second_messages = [
        {
            "ts": "222.222",
            "user": "U123",
            "channel": "frontend",
            "text": "Here is my HTML snippet",
        }
    ]
    user_profiles = {
        "U999": {"id": "U999", "name": "david", "real_name": "David"},
        "U123": {"id": "U123", "name": "anna.bob", "real_name": "Anna Bob"},
    }

    async def fake_get_messages_by_topic(topic, timeframe_days=30, channels=None):
        if topic == "What does Anna Bob talk about?":
            return first_messages
        if topic in {'from:"Anna Bob"', '"Anna Bob"', 'Anna Bob'}:
            return second_messages
        return []

    with patch.object(
        analysis_service.slack_service,
        "get_messages_by_topic",
        new=AsyncMock(side_effect=fake_get_messages_by_topic),
    ) as mock_get_messages, \
         patch.object(analysis_service.slack_service, "get_user_profiles", new=AsyncMock(return_value=user_profiles)), \
         patch.object(
             analysis_service.ollama_client,
             "custom_analysis",
             new=AsyncMock(
                 return_value={
                     "insights": "Anna Bob mostly shares HTML examples.",
                     "relevant_users": [],
                     "key_messages": []
                 }
             ),
         ) as mock_custom_analysis:
        result = await analysis_service.custom_analysis("What does Anna Bob talk about?")

    searched_terms = [call.kwargs["topic"] for call in mock_get_messages.await_args_list]
    assert len(searched_terms) > 1
    assert 'from:"Anna Bob"' in searched_terms
    analyzed_messages = mock_custom_analysis.await_args.kwargs["messages"]
    assert len(analyzed_messages) == 2
    assert result.insights == "Anna Bob mostly shares HTML examples."


@pytest.mark.asyncio
async def test_find_experts_default_min_messages_includes_single_match():
    """Default expert lookup should include a real helper even with only one matching message."""
    cache_manager.clear()
    messages = [
        {
            "ts": "123.456",
            "user": "U123",
            "channel": "frontend",
            "text": "<html><body>Snake Game</body></html>"
        }
    ]
    user_profiles = {
        "U123": {
            "id": "U123",
            "name": "anna.bob",
            "real_name": "Anna Bob"
        }
    }

    with patch.object(analysis_service.slack_service, "get_messages_by_topic", new=AsyncMock(return_value=messages)), \
         patch.object(analysis_service.slack_service, "get_user_profiles", new=AsyncMock(return_value=user_profiles)), \
         patch.object(analysis_service.slack_service, "aggregate_user_activity", new=AsyncMock(return_value={"U123": {"message_count": 1, "messages": messages}})), \
         patch.object(
             analysis_service.ollama_client,
             "analyze_expertise",
             new=AsyncMock(return_value={
                 "experts": [
                     {
                         "user_id": "U123",
                         "expertise_score": 0.91,
                         "key_topics": ["HTML"],
                         "analysis": "Anna shared working HTML code."
                     }
                 ]
             })
         ):
        result = await analysis_service.find_experts("HTML")

    assert result.total_found == 1
    assert result.experts[0].user.real_name == "Anna Bob"
    assert result.experts[0].message_count == 1


@pytest.mark.asyncio
async def test_find_experts_falls_back_when_ollama_returns_no_experts():
    """If Ollama fails to rank experts, the service should still return qualified Slack matches."""
    cache_manager.clear()
    messages = [
        {
            "ts": "123.456",
            "user": "U123",
            "channel": "frontend",
            "text": "<!doctype html><html><body>Snake Game</body></html>",
            "reactions": [],
            "reply_count": 0,
        }
    ]
    user_profiles = {
        "U123": {
            "id": "U123",
            "name": "anna.bob",
            "real_name": "Anna Bob",
        }
    }

    with patch.object(analysis_service.slack_service, "get_messages_by_topic", new=AsyncMock(return_value=messages)), \
         patch.object(analysis_service.slack_service, "get_user_profiles", new=AsyncMock(return_value=user_profiles)), \
         patch.object(
             analysis_service.slack_service,
             "aggregate_user_activity",
             new=AsyncMock(return_value={
                 "U123": {
                     "message_count": 1,
                     "thread_count": 0,
                     "reaction_count": 0,
                     "messages": messages,
                 }
             }),
         ), \
         patch.object(
             analysis_service.ollama_client,
             "analyze_expertise",
             new=AsyncMock(return_value={"experts": []}),
         ):
        result = await analysis_service.find_experts("HTML")

    assert result.total_found == 1
    assert result.experts[0].user.real_name == "Anna Bob"
    assert result.experts[0].key_topics == ["HTML"]
    assert "Anna Bob mentioned HTML" in result.experts[0].analysis


def test_convert_to_message_summary_handles_channel_dict():
    """Slack search results may provide channel metadata as a dict instead of a string."""
    summary = slack_service.convert_to_message_summary(
        {
            "ts": "123.456",
            "user": "U123",
            "channel": {"id": "C123", "name": "engineering"},
            "text": "Deployment note"
        }
    )

    assert summary.channel == "engineering"


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
