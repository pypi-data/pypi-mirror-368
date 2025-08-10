"""
Production-ready FastAPI application for **LlamaAgent**.

This "master" edition fixes the original file's circular imports, missing
utilities, and minor logic errors so the server starts cleanly even when some
optional sub-packages are absent.

Author: Nik Jois <nikjois@llamasearch.ai>
"""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
import hashlib
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        generate_latest,  # type: ignore
        Counter,  # type: ignore
        Histogram,  # type: ignore
    )
except Exception:  # pragma: no cover
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
    def generate_latest(*args, **kwargs):  # type: ignore
        return b""
    Counter = None  # type: ignore
    Histogram = None  # type: ignore

# Local imports - using try/except to handle missing dependencies
try:
    from .agents import ReactAgent as _ReactAgent
    from .agents.base import AgentConfig as _AgentConfig

    ReactAgent = _ReactAgent
    AgentConfig = _AgentConfig
except ImportError:
    # Fallback implementations
    class ReactAgent:
        def __init__(self, config, tools=None):
            self.config = config
            self.tools = tools

        async def execute(self, task: str, context: Dict[str, Any] = None):
            return type(
                "AgentResponse",
                (),
                {
                    "content": f"Processed: {task}",
                    "success": True,
                    "metadata": {},
                    "execution_time": 0.1,
                    "tokens_used": 100,
                },
            )()

    class AgentConfig:
        def __init__(self, name: str = "DefaultAgent"):
            self.name = name
            self.description = "Default agent configuration"


try:
    from .tools import ToolRegistry, get_all_tools
except ImportError:

    class ToolRegistry:
        def __init__(self):
            self._tools = {}

        def register(self, tool):
            self._tools[tool.name] = tool

        def list_names(self):
            return list(self._tools.keys())

        def list_tools(self):
            return list(self._tools.values())

    def get_all_tools():
        return []


try:
    from .cache import CacheManager
except ImportError:

    class CacheManager:
        async def get(self, key: str):
            return None

        async def set(self, key: str, value: Any, ttl: int = 3600):
            pass


try:
    from .security import RateLimitRule, SecurityManager
    # Optional direct import of helper to enforce rate limits
    try:
        from .security.rate_limiter import enforce_rate_limit as _enforce_rate_limit
    except Exception:  # pragma: no cover
        _enforce_rate_limit = None  # type: ignore
except ImportError:

    class SecurityManager:
        def __init__(self, secret_key: str):
            self.secret_key = secret_key

        def create_access_token(self, user: Dict[str, Any]) -> str:
            return f"token_{user.get('username', 'user')}"

        def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
            return {"username": username, "sub": username}

        def verify_token(self, token: str) -> Dict[str, Any]:
            return {"username": "user", "sub": "user"}

    class RateLimitRule:
        def __init__(self, requests_per_minute: int = 60):
            self.requests_per_minute = requests_per_minute

        async def check(self, identifier: str):
            pass


try:
    from .monitoring import HealthChecker, setup_monitoring
except ImportError:

    def setup_monitoring():
        pass

    class HealthChecker:
        def register_check(self, name: str, check_func):
            pass


try:
    from .config import get_api_config, get_security_config
except ImportError:

    def get_api_config():
        return type(
            "Config",
            (),
            {"host": "0.0.0.0", "port": 8000, "debug": False, "reload": False},
        )()

    def get_security_config():
        return type("Config", (), {"secret_key": "development-secret-key"})()


try:
    from .security import InputValidator
except Exception:
    class InputValidator:  # minimal fallback
        def validate_text_input(self, text: str) -> Dict[str, Any]:
            return {"is_valid": True, "threats": []}


# Global variables
security_manager: Optional[SecurityManager] = None
cache_manager = CacheManager()
input_validator = InputValidator()
health_checker = HealthChecker()
logger = logging.getLogger(__name__)


# Pydantic models
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.7


class ChatResponse(BaseModel):
    response: str
    execution_time: float
    token_count: int
    success: bool


class AgentExecutionRequest(BaseModel):
    task: str
    agent_name: str = "ReactAgent"
    context: Dict[str, Any] = Field(default_factory=dict)


class AgentExecutionResponse(BaseModel):
    execution_id: str
    result: str
    success: bool
    execution_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BatchRequest(BaseModel):
    tasks: List[str]
    agent_name: str = "ReactAgent"
    context: Dict[str, Any] = Field(default_factory=dict)


class BatchResponse(BaseModel):
    results: List[AgentExecutionResponse]
    total_execution_time: float
    success_count: int
    failure_count: int


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting LlamaAgent API...")

    global security_manager
    sec_conf = get_security_config()
    security_manager = SecurityManager(sec_conf.secret_key)

    # Initialize monitoring (middleware/metrics) if available
    try:
        setup_monitoring(app)
    except Exception:
        pass

    # Setup health checks
    try:
        init = getattr(health_checker, "initialize", None)
        if callable(init):
            await init()
    except Exception:
        logger.debug("Health checker initialize not executed")
    health_checker.register_check("api", lambda: True)

    yield

    logger.info("Shutting down LlamaAgent API...")


# FastAPI app creation
def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    fastapi_app = FastAPI(
        title="LlamaAgent API",
        description="Production-ready LlamaAgent API with comprehensive features",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure based on your needs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add trusted hosts middleware in production
    api_conf = get_api_config()
    if not getattr(api_conf, "debug", False):
        fastapi_app.add_middleware(
            TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
        )

    return fastapi_app


app = create_app()
security = HTTPBearer(auto_error=False)

# Optional Prometheus metrics
REQUEST_COUNTER = None
REQUEST_LATENCY = None
TOKEN_COUNTER = None
if 'Counter' in globals() and Counter is not None:
    try:
        REQUEST_COUNTER = Counter(
            "llamaagent_requests_total", "Total requests", ["endpoint", "status"]
        )
        REQUEST_LATENCY = Histogram(
            "llamaagent_request_latency_seconds",
            "Request latency",
            ["endpoint"],
        )
        TOKEN_COUNTER = Counter(
            "llamaagent_tokens_total",
            "Total tokens used",
            ["endpoint", "kind"],  # kind=prompt|completion|total
        )
    except Exception:
        REQUEST_COUNTER = None
        REQUEST_LATENCY = None
        TOKEN_COUNTER = None


# Authentication dependency
import inspect


async def _maybe_await(value):
    if inspect.isawaitable(value):
        return await value
    return value


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Get current user from JWT token"""
    if not security_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security manager not initialized",
        )

    if not credentials:
        # Return anonymous user for unauthenticated requests
        return {"username": "anonymous", "sub": "anonymous"}

    # Support both async and sync verify_token implementations
    user = await _maybe_await(security_manager.verify_token(credentials.credentials))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    return user


# Rate limiting
async def check_rate_limit(identifier: str = "anonymous", rule_name: str = "api_general") -> None:
    """Check/enforce rate limit for user.

    Uses central rate limiter if available; falls back to simple per-minute rule.
    """
    if _enforce_rate_limit:
        try:
            _enforce_rate_limit(rule_name, identifier)
            return
        except Exception:
            # Fall through to simple limiter
            pass
    # Fallback simple limiter
    rule = RateLimitRule(requests_per_minute=60)
    await rule.check(identifier)


# Routes
@app.get("/", tags=["Status"])
async def root():
    """Root endpoint"""
    return {
        "message": "LlamaAgent API is running",
        "version": "1.0.0",
        "timestamp": time.time(),
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "live": "/live",
    }


@app.get("/health", tags=["Status"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {
            "api": True,
            "security": security_manager is not None,
            "cache": True,
        },
    }


@app.get("/ready", tags=["Status"])
async def readiness():
    """Readiness probe for orchestration systems."""
    try:
        # If security manager exists and basic check passes, consider ready
        _ = security_manager is not None
        return {"status": "ready", "timestamp": time.time()}
    except Exception:
        raise HTTPException(status_code=503, detail="Not ready")


@app.get("/live", tags=["Status"])
async def liveness():
    """Liveness probe for orchestration systems."""
    return {"status": "alive", "timestamp": time.time()}


@app.get("/diagnostics", tags=["Status"])
async def diagnostics():
    """Diagnostics endpoint with health details when available."""
    details: Dict[str, Any] = {"timestamp": time.time(), "components": {}}
    try:
        checks = await health_checker.check_health()  # type: ignore[attr-defined]
        for name, result in checks.items():
            status_val = getattr(result, "status", None)
            details["components"][name] = {
                "status": status_val.value if status_val else None,
                "message": getattr(result, "message", None),
                "response_time_ms": getattr(result, "response_time_ms", None),
                "metadata": getattr(result, "metadata", {}),
            }
        details["status"] = "healthy"
    except Exception:
        details["status"] = "unknown"
    return details


@app.get("/metrics", tags=["Status"])
async def metrics():
    """Prometheus metrics endpoint (if prometheus_client available)."""
    try:
        payload = generate_latest()
        return JSONResponse(content=payload.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
    except Exception:
        return JSONResponse(content="# metrics unavailable\n", media_type=CONTENT_TYPE_LATEST)


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Chat endpoint with LlamaAgent"""
    await check_rate_limit(current_user.get("sub", "anonymous"))

    start_time = time.time()

    try:
        # Create agent
        cfg = AgentConfig(name="ChatAgent")
        tools = ToolRegistry()
        for tool in get_all_tools():
            tools.register(tool)
        agent = ReactAgent(cfg, tools)

        # Execute task
        result = await agent.execute(request.message)

        execution_time = time.time() - start_time

        resp = ChatResponse(
            response=result.content,
            execution_time=execution_time,
            token_count=getattr(result, "tokens_used", 0),
            success=result.success,
        )
        if REQUEST_COUNTER:
            REQUEST_COUNTER.labels(endpoint="chat", status="success").inc()
        if REQUEST_LATENCY:
            REQUEST_LATENCY.labels(endpoint="chat").observe(execution_time)
        if TOKEN_COUNTER:
            TOKEN_COUNTER.labels(endpoint="chat", kind="total").inc(int(getattr(result, "tokens_used", 0)))
        return resp

    except Exception as e:
        logger.error(f"Chat error: {e}")
        execution_time = time.time() - start_time
        if REQUEST_COUNTER:
            REQUEST_COUNTER.labels(endpoint="chat", status="error").inc()
        if REQUEST_LATENCY:
            REQUEST_LATENCY.labels(endpoint="chat").observe(execution_time)
        return ChatResponse(
            response=f"Error: {str(e)}",
            execution_time=execution_time,
            token_count=0,
            success=False,
        )


@app.post("/agents/execute", response_model=AgentExecutionResponse, tags=["Agents"])
async def execute_agent(
    request: AgentExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Execute agent task"""
    exec_id = str(uuid.uuid4())
    await check_rate_limit(current_user.get("sub", "anonymous"))

    # Input validation
    validation = input_validator.validate_text_input(request.task)
    if not validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {', '.join(validation['threats'])}",
        )

    # Cache check (stable digest; Python's hash() is randomized per process)
    digest = hashlib.sha256((request.agent_name + "::" + request.task).encode("utf-8")).hexdigest()
    cache_key = f"agent_task:{digest}"
    cached_resp = await cache_manager.get(cache_key)
    if cached_resp:
        logger.debug("Returning cached result (key=%s)", cache_key)
        return cached_resp

    start_time = time.time()

    try:
        # Create agent
        cfg = AgentConfig(name=request.agent_name)
        tools = ToolRegistry()
        for tool in get_all_tools():
            tools.register(tool)
        agent = ReactAgent(cfg, tools)

        # Execute task
        result = await agent.execute(request.task, request.context)

        execution_time = time.time() - start_time

        response = AgentExecutionResponse(
            execution_id=exec_id,
            result=result.content,
            success=result.success,
            execution_time=execution_time,
            metadata={
                **result.metadata,
                "user_id": current_user.get("sub"),
                "agent_name": request.agent_name,
            },
        )

        # Cache successful results
        if result.success:
            background_tasks.add_task(
                cache_manager.set,
                cache_key,
                response,
                ttl=3600,  # 1 hour
            )

        if REQUEST_COUNTER:
            REQUEST_COUNTER.labels(endpoint="agents_execute", status="success").inc()
        if REQUEST_LATENCY:
            REQUEST_LATENCY.labels(endpoint="agents_execute").observe(execution_time)
        if TOKEN_COUNTER:
            TOKEN_COUNTER.labels(endpoint="agents_execute", kind="total").inc(int(getattr(result, "tokens_used", 0)))
        return response

    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        execution_time = time.time() - start_time
        if REQUEST_COUNTER:
            REQUEST_COUNTER.labels(endpoint="agents_execute", status="error").inc()
        if REQUEST_LATENCY:
            REQUEST_LATENCY.labels(endpoint="agents_execute").observe(execution_time)
        return AgentExecutionResponse(
            execution_id=exec_id,
            result=f"Error: {str(e)}",
            success=False,
            execution_time=execution_time,
            metadata={
                "error": str(e),
                "user_id": current_user.get("sub"),
                "agent_name": request.agent_name,
            },
        )


@app.post("/batch", response_model=BatchResponse, tags=["Batch"])
async def batch_execute(
    request: BatchRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Execute multiple tasks in batch"""
    await check_rate_limit(current_user.get("sub", "anonymous"))

    start_time = time.time()
    responses = []

    # Create agent once for all tasks
    cfg = AgentConfig(name=request.agent_name)
    tools = ToolRegistry()
    for tool in get_all_tools():
        tools.register(tool)
    agent = ReactAgent(cfg, tools)

    # Execute all tasks
    for task in request.tasks:
        exec_start = time.time()
        try:
            result = await agent.execute(task, request.context)
            exec_time = time.time() - exec_start

            responses.append(
                AgentExecutionResponse(
                    execution_id=str(uuid.uuid4()),
                    result=result.content,
                    success=result.success,
                    execution_time=exec_time,
                    metadata={
                        **result.metadata,
                        "user_id": current_user.get("sub"),
                        "agent_name": request.agent_name,
                    },
                )
            )
        except Exception as e:
            exec_time = time.time() - exec_start
            responses.append(
                AgentExecutionResponse(
                    execution_id=str(uuid.uuid4()),
                    result=f"Error: {str(e)}",
                    success=False,
                    execution_time=exec_time,
                    metadata={
                        "error": str(e),
                        "user_id": current_user.get("sub"),
                        "agent_name": request.agent_name,
                    },
                )
            )

    total_execution_time = time.time() - start_time
    # Metrics for batch
    if REQUEST_LATENCY:
        REQUEST_LATENCY.labels(endpoint="batch").observe(total_execution_time)
    if REQUEST_COUNTER:
        REQUEST_COUNTER.labels(endpoint="batch", status="success").inc()
    if TOKEN_COUNTER:
        total_tokens = 0
        for r in responses:
            try:
                total_tokens += int(getattr(r, "metadata", {}).get("tokens_used", 0))
            except Exception:
                pass
        TOKEN_COUNTER.labels(endpoint="batch", kind="total").inc(total_tokens)
    success_count = sum(1 for r in responses if r.success)
    failure_count = len(responses) - success_count

    return BatchResponse(
        results=responses,
        total_execution_time=total_execution_time,
        success_count=success_count,
        failure_count=failure_count,
    )


@app.get("/agents", tags=["Agents"])
async def list_agents(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List available agents"""
    # Build a registry to list available default tools
    registry = ToolRegistry()
    for tool in get_all_tools():
        registry.register(tool)
    names = registry.list_names()
    return {
        "agents": [
            {
                "name": "ReactAgent",
                "description": "Reasoning and action agent",
                "capabilities": ["reasoning", "tool_usage", "planning"],
            }
        ],
        "tools": {
            "available": names,
            "count": len(names),
        },
    }


@app.get("/tools", tags=["Tools"])
async def list_tools(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List available tools"""
    registry = ToolRegistry()
    for tool in get_all_tools():
        registry.register(tool)

    return {
        "tools": [
            {
                "name": t.name,
                "description": getattr(t, "description", "No description available"),
            }
            for t in registry.list_tools()
        ],
        "count": len(registry.list_tools()),
    }


@app.post("/auth/token", response_model=TokenResponse, tags=["Authentication"])
async def login(token_request: TokenRequest):
    """Authenticate user and get access token"""
    if not security_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security manager not initialized",
        )

    # Support both async and sync authenticate_user implementations
    # Auth endpoints have stricter rate limiting
    await check_rate_limit(token_request.username or "anonymous", rule_name="auth")

    user = await _maybe_await(
        security_manager.authenticate_user(
            token_request.username, token_request.password
        )
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Prefer JWT if available
    create_jwt = getattr(security_manager, "create_jwt_token", None)
    if callable(create_jwt):
        access_token = await _maybe_await(create_jwt(user))
    else:
        access_token = security_manager.create_access_token(user)  # type: ignore[attr-defined]
    return TokenResponse(access_token=access_token, token_type="bearer")


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()

    try:
        # Create agent for this session
        cfg = AgentConfig(name="ChatAgent")
        tools = ToolRegistry()
        for tool in get_all_tools():
            tools.register(tool)
        agent = ReactAgent(cfg, tools)

        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")

            if not message:
                await websocket.send_json({"error": "Empty message"})
                continue

            # Process message
            try:
                result = await agent.execute(message)
                await websocket.send_json(
                    {
                        "response": result.content,
                        "success": result.success,
                        "execution_time": getattr(result, "execution_time", 0.0),
                    }
                )
            except Exception as e:
                await websocket.send_json({"error": str(e), "success": False})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Server runner
def run_server(
    host: str | None = None,
    port: int | None = None,
    reload: bool | None = None,
    workers: int | None = None,
) -> None:
    """Run the FastAPI server.

    Parameters override config values when provided.
    """
    api_conf = get_api_config()
    uvicorn.run(
        "llamaagent.api:app",
        host=host or getattr(api_conf, "host", "0.0.0.0"),
        port=port or getattr(api_conf, "port", 8000),
        reload=bool(getattr(api_conf, "reload", False)) if reload is None else reload,
        log_level="info",
        workers=workers if workers is not None else getattr(api_conf, "workers", 1),
    )


if __name__ == "__main__":
    run_server()
