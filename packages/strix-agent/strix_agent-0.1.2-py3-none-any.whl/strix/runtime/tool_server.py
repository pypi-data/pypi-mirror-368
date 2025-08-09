import logging
import os
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ValidationError


SANDBOX_MODE = os.getenv("STRIX_SANDBOX_MODE", "false").lower() == "true"
if not SANDBOX_MODE:
    raise RuntimeError("Tool server should only run in sandbox mode (STRIX_SANDBOX_MODE=true)")

EXPECTED_TOKEN = os.getenv("STRIX_SANDBOX_TOKEN")
if not EXPECTED_TOKEN:
    raise RuntimeError("STRIX_SANDBOX_TOKEN environment variable is required in sandbox mode")

app = FastAPI()
logger = logging.getLogger(__name__)
security = HTTPBearer()

security_dependency = Depends(security)


def verify_token(credentials: HTTPAuthorizationCredentials) -> str:
    if not credentials or credentials.scheme != "Bearer":
        logger.warning("Authentication failed: Invalid or missing Bearer token scheme")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.credentials != EXPECTED_TOKEN:
        logger.warning("Authentication failed: Invalid token provided from remote host")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("Authentication successful for tool execution request")
    return credentials.credentials


class ToolExecutionRequest(BaseModel):
    tool_name: str
    kwargs: dict[str, Any]


class ToolExecutionResponse(BaseModel):
    result: Any | None = None
    error: str | None = None


@app.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    request: ToolExecutionRequest, credentials: HTTPAuthorizationCredentials = security_dependency
) -> ToolExecutionResponse:
    verify_token(credentials)

    from strix.tools.argument_parser import ArgumentConversionError, convert_arguments
    from strix.tools.registry import get_tool_by_name

    try:
        tool_func = get_tool_by_name(request.tool_name)
        if not tool_func:
            return ToolExecutionResponse(error=f"Tool '{request.tool_name}' not found")

        converted_kwargs = convert_arguments(tool_func, request.kwargs)

        result = tool_func(**converted_kwargs)

        return ToolExecutionResponse(result=result)

    except (ArgumentConversionError, ValidationError) as e:
        logger.warning("Invalid tool arguments: %s", e)
        return ToolExecutionResponse(error=f"Invalid arguments: {e}")
    except TypeError as e:
        logger.warning("Tool execution type error: %s", e)
        return ToolExecutionResponse(error=f"Tool execution error: {e}")
    except ValueError as e:
        logger.warning("Tool execution value error: %s", e)
        return ToolExecutionResponse(error=f"Tool execution error: {e}")
    except Exception:
        logger.exception("Unexpected error during tool execution")
        return ToolExecutionResponse(error="Internal server error")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "sandbox_mode": str(SANDBOX_MODE),
        "environment": "sandbox" if SANDBOX_MODE else "main",
        "auth_configured": "true" if EXPECTED_TOKEN else "false",
    }
