"""Services module."""
from app.services.slack_client import slack_client
from app.services.ollama_client import ollama_client
from app.services.slack_service import slack_service

__all__ = ["slack_client", "ollama_client", "slack_service"]

# Made with Bob
