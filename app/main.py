"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.api import router
from app.config import settings
from app.services.slack_client import slack_client
from app.utils.logger import setup_logger
from app import __version__

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Bobager API...")
    try:
        await slack_client.connect()
        logger.info("Connected to Slack API")
    except Exception as e:
        logger.error(f"Failed to connect to Slack API: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bobager API...")
    try:
        await slack_client.disconnect()
        logger.info("Disconnected from Slack API")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Bobager API",
    description="""
    Slack + Ollama LLM Integration API
    
    This API connects to your Slack workspace and uses Ollama (local LLM) to analyze
    chat history, identify experts, and find key contributors.
    
    ## Features
    
    * **Find Experts**: Identify subject matter experts on specific technologies or topics
    * **Analyze Contributors**: Discover key contributors in channels
    * **Custom Analysis**: Perform flexible analysis with natural language queries
    * **Caching**: Built-in caching for improved performance
    * **Privacy**: All LLM processing happens locally via Ollama
    
    ## Authentication
    
    Currently, this API does not require authentication. In production, you should
    implement proper authentication and authorization.
    """,
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Analysis"])

# Mount static files
static_dir = Path(__file__).parent.parent
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

# Made with Bob
