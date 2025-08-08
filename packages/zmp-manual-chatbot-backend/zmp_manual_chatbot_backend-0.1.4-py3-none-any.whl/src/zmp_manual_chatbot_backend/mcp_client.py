# NOTE: You must add 'fastmcp' to your pyproject.toml dependencies for this client to work.
from typing import Any, Dict, List, Optional
from .config import settings
import asyncio

try:
    from fastmcp import Client as FastMCPClient
except ImportError:
    FastMCPClient = None  # Placeholder for type checking

class MCPClient:
    """
    Official MCP client using FastMCP (https://gofastmcp.com/clients/client).
    Usage:
        async with MCPClient() as client:
            result = await client.call_tool("search_knowledge", {"query": query, ...})
    """
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.MCP_SERVER_URL.rstrip("/")
        self._client: Optional[FastMCPClient] = None

    async def __aenter__(self):
        if FastMCPClient is None:
            raise ImportError("fastmcp is not installed. Please add it to your dependencies.")
        self._client = FastMCPClient(self.base_url)
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._client:
            await self._client.__aexit__(exc_type, exc, tb)
            self._client = None

    async def call_tool(self, tool_name: str, payload: Dict[str, Any], retry: int = 3, delay: float = 1.0) -> Any:
        """
        Call an MCP tool endpoint using FastMCP's call_tool method.
        Retries on failure.
        Returns the raw result (see FastMCP docs for details).
        """
        for attempt in range(retry):
            try:
                if not self._client:
                    raise RuntimeError("MCPClient must be used as an async context manager.")
                result = await self._client.call_tool(tool_name, payload)
                return result
            except Exception as e:
                if attempt < retry - 1:
                    await asyncio.sleep(delay)
                else:
                    raise e
        return None

    @staticmethod
    def extract_structured_content(result: Any) -> Any:
        """
        Helper to extract 'structured_content' from a FastMCP CallToolResult, if present.
        """
        if hasattr(result, 'structured_content'):
            return result.structured_content
        return result

    async def health_check(self) -> Dict[str, Any]:
        """
        Ping the MCP server to check connectivity.
        """
        if not self._client:
            raise RuntimeError("MCPClient must be used as an async context manager.")
        try:
            await self._client.ping()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
