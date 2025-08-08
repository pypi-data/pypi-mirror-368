from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from .router import router
from .auth_router import router as auth_router
from .service import ChatbotService
from contextlib import asynccontextmanager
from .config import settings
from .utils import ensure_ollama_running, ensure_ollama_model_pulled
import traceback
from .session import SessionManager
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown tasks.
    """
    try:
        print("🚀 Starting ZMP Manual Chatbot Backend...")
        print(f"🔧 LLM Provider: {settings.LLM_PROVIDER}")
        
        # Determine effective provider
        print("📋 Determining effective LLM provider...")
        provider = settings.effective_llm_provider
        print(f"📋 Effective LLM Provider: {provider}")
        
        if provider == "ollama":
            print("🔧 Setting up Ollama...")
            
            print("  ⏳ Checking if Ollama service is running...")
            if not ensure_ollama_running():
                raise RuntimeError("Failed to start Ollama service")
            print("  ✅ Ollama service is running")
            
            print(f"  ⏳ Checking if model {settings.OLLAMA_MODEL} is available...")
            if not ensure_ollama_model_pulled(settings.OLLAMA_MODEL):
                raise RuntimeError(f"Failed to setup Ollama model: {settings.OLLAMA_MODEL}")
            print(f"  ✅ Model {settings.OLLAMA_MODEL} is available")
            
            print(f"✅ Ollama ready with model: {settings.OLLAMA_MODEL}")
            
            # Display memory usage info
            model_size_info = {
                "qwen2:1.5b": "~0.9GB",
                "llama3.2:1b": "~1.3GB", 
                "gemma2:2b": "~1.6GB",
                "llama3.2:3b": "~2GB",
                "phi3:mini": "~2.3GB"
            }
            estimated_size = model_size_info.get(settings.OLLAMA_MODEL, "Unknown")
            print(f"📊 Estimated model size: {estimated_size}")
         
        elif provider == "openai":
            print("🔧 Setting up OpenAI...")
            if settings.OPENAI_API_KEY:
                print(f"✅ OpenAI API configured with model: {settings.OPENAI_MODEL}")
            else:
                print("⚠️  WARNING: OPENAI_API_KEY not set")
        
        print("🧪 Testing LLM initialization...")
        try:
            from .utils import get_llm
            llm = get_llm()
            print(f"✅ LLM initialized successfully: {type(llm)}")
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            traceback.print_exc()
            raise
        
        # Simple Authentication Callback Available
        print("🔐 OAuth2 authentication callback available at /api/manual-chatbot/v1/auth/callback")
        print(f"🔒 Keycloak server: {settings.KEYCLOAK_SERVER_URL}")
        print(f"🏰 Keycloak realm: {settings.KEYCLOAK_REALM}")
        
        # Initialize ChatbotService and generate workflow graph
        app.state.chatbot_service = await ChatbotService.async_init()
        # Initialize SessionManager
        app.state.session_manager = SessionManager()
        # Start session cleanup task
        await app.state.session_manager.start_cleanup_task()
        print("✅ ChatbotService initialized and workflow graph generated (workflow_graph.png)")
        print("✅ SessionManager initialized with cleanup task")
        
        print("✅ Backend startup complete!")
        yield
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        traceback.print_exc()
        raise
    
    print("🛑 Shutting down ZMP Manual Chatbot Backend...")
    # Stop session cleanup task
    if hasattr(app.state, 'session_manager'):
        await app.state.session_manager.stop_cleanup_task()
    # Add any cleanup logic here if needed

logger = logging.getLogger("appLogger")

# Create FastAPI application
app = FastAPI(
    title="ZMP Manual Chatbot Backend", 
    description="Backend service for ZMP manual chatbot",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/manual-chatbot/v1/api-docs",
    openapi_url="/api/manual-chatbot/v1/openapi.json",
    default_response_class=JSONResponse,
    debug=True,
    root_path_in_servers=True,
)

# Custom OpenAPI schema function to match reference implementation
def custom_openapi():
    """Custom OpenAPI schema generator matching the reference implementation"""
    # Always regenerate the schema to ensure we have the latest configuration
    app.openapi_schema = None

    # Get application root and port from settings
    app_port = "5370"  # Our server port
    app_url = f"http://localhost:{app_port}"

    # Define Keycloak endpoints
    auth_url = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/auth"
    token_url = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
    userinfo_url = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/userinfo"

    # Define redirect URL for Swagger UI - built-in Swagger UI redirect path
    swagger_redirect_url = f"{app_url}/api/manual-chatbot/v1/api-docs/oauth2-redirect"

    # Log the OAuth2 configuration
    logger.info("OAuth2 configuration for OpenAPI schema:")
    logger.info(f"- Authorization URL: {auth_url}")
    logger.info(f"- Token URL: {token_url}")
    logger.info(f"- Userinfo URL: {userinfo_url}")
    logger.info(f"- Client ID: {settings.KEYCLOAK_CLIENT_ID}")
    logger.info(f"- Swagger Redirect URL: {swagger_redirect_url}")

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        openapi_version="3.0.0",  # Downgrade to 3.0.0 like reference
        servers=app.servers,
    )

    # Add security schemes
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    # Completely reset security schemes to avoid any default values
    openapi_schema["components"]["securitySchemes"] = {}

    # Add OAuth2 security scheme matching the reference implementation
    openapi_schema["components"]["securitySchemes"]["OAuth2AuthorizationCodeBearer"] = {
        "type": "oauth2",
        "flows": {
            "authorizationCode": {
                "refreshUrl": userinfo_url,
                "scopes": {},  # Empty scopes like reference
                "authorizationUrl": auth_url,
                "tokenUrl": token_url,
            }
        },
    }

    # Add HTTP Basic security scheme like the reference
    openapi_schema["components"]["securitySchemes"]["HTTPBasic"] = {
        "type": "http",
        "scheme": "basic",
    }

    # Add security requirements to specific endpoints
    if "paths" in openapi_schema:
        # Add OAuth2 security requirement to chat endpoint
        chat_endpoint_path = "/api/manual-chatbot/v1/chat/query"
        if chat_endpoint_path in openapi_schema["paths"]:
            if "post" in openapi_schema["paths"][chat_endpoint_path]:
                openapi_schema["paths"][chat_endpoint_path]["post"]["security"] = [
                    {"OAuth2AuthorizationCodeBearer": []},
                    {"HTTPBasic": []}
                ]
                logger.info(f"Added security requirements to {chat_endpoint_path}")

    # Set the schema on the app
    app.openapi_schema = openapi_schema

    # Log that we've successfully set the OpenAPI schema
    logger.info("Successfully set custom OpenAPI schema with Keycloak security schemes")

    return app.openapi_schema

app.openapi = custom_openapi

# Include routers with base path prefix
app.include_router(router, prefix="/api/manual-chatbot/v1")  # Main chat router  
app.include_router(auth_router)  # Authentication router (already has prefix)
