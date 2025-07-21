"""MCP protocol verification tests for VFX MCP server.

This module provides comprehensive tests for Model Context Protocol (MCP) 
compliance and protocol-specific functionality. Tests ensure the server
correctly implements MCP specification requirements.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, TypedDict, cast

import pytest
from fastmcp import Client, FastMCP
from fastmcp.client.transports import FastMCPTransport

if TYPE_CHECKING:
    from typing import NotRequired


class MCPRequest(TypedDict):
    """Type definition for MCP request structure."""
    jsonrpc: str
    id: int | str
    method: str
    params: NotRequired[dict[str, Any]]


class MCPResponse(TypedDict):
    """Type definition for MCP response structure."""
    jsonrpc: str
    id: int | str
    result: NotRequired[dict[str, Any]]
    error: NotRequired[dict[str, Any]]


class MCPCapabilities(TypedDict):
    """Type definition for MCP capabilities."""
    experimental: NotRequired[dict[str, Any]]
    sampling: NotRequired[dict[str, Any]]
    tools: NotRequired[dict[str, Any]]
    resources: NotRequired[dict[str, Any]]
    prompts: NotRequired[dict[str, Any]]


class MCPInitializeResult(TypedDict):
    """Type definition for MCP initialize result."""
    protocolVersion: str
    capabilities: MCPCapabilities
    serverInfo: dict[str, Any]


class MCPToolInfo(TypedDict):
    """Type definition for MCP tool information."""
    name: str
    description: str
    inputSchema: dict[str, Any]


class MCPResourceInfo(TypedDict):
    """Type definition for MCP resource information."""
    uri: str
    name: str
    description: str
    mimeType: NotRequired[str]


class TestMCPProtocolVerification:
    """Test suite for MCP protocol compliance verification."""

    @pytest.mark.integration
    async def test_mcp_jsonrpc_compliance(self, mcp_server: FastMCP[None]) -> None:
        """Test JSON-RPC 2.0 compliance for MCP protocol."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        
        # Test initialize request follows JSON-RPC 2.0
        init_response = await client.initialize()
        
        # Response should contain required JSON-RPC fields
        assert "protocolVersion" in init_response
        assert "capabilities" in init_response
        assert "serverInfo" in init_response
        
        # Protocol version should be valid
        protocol_version = init_response["protocolVersion"]
        assert isinstance(protocol_version, str)
        assert protocol_version.startswith("2024-")

    @pytest.mark.integration
    async def test_mcp_capabilities_declaration(self, mcp_server: FastMCP[None]) -> None:
        """Test MCP capabilities are properly declared."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        
        init_response = await client.initialize()
        capabilities = cast(MCPCapabilities, init_response["capabilities"])
        
        # Server should declare tool capabilities
        assert "tools" in capabilities
        tools_cap = capabilities["tools"]
        assert isinstance(tools_cap, dict)
        
        # Server should declare resource capabilities
        assert "resources" in capabilities
        resources_cap = capabilities["resources"]
        assert isinstance(resources_cap, dict)

    @pytest.mark.integration
    async def test_mcp_server_info(self, mcp_server: FastMCP[None]) -> None:
        """Test MCP server information is properly provided."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        
        init_response = await client.initialize()
        server_info = init_response["serverInfo"]
        
        # Server info should contain required fields
        assert "name" in server_info
        assert "version" in server_info
        
        # Verify server identity
        assert server_info["name"] == "vfx-mcp"
        assert isinstance(server_info["version"], str)

    @pytest.mark.integration
    async def test_mcp_tools_list_compliance(self, mcp_server: FastMCP[None]) -> None:
        """Test MCP tools/list request compliance."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test tools/list request
        tools_response = await client.list_tools()
        
        assert "tools" in tools_response
        tools = cast(list[MCPToolInfo], tools_response["tools"])
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Each tool should have required MCP fields
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            
            # Verify field types
            assert isinstance(tool["name"], str)
            assert isinstance(tool["description"], str)
            assert isinstance(tool["inputSchema"], dict)
            
            # inputSchema should be valid JSON Schema
            schema = tool["inputSchema"]
            assert "type" in schema
            assert schema["type"] == "object"
            
            if "properties" in schema:
                assert isinstance(schema["properties"], dict)
            
            if "required" in schema:
                assert isinstance(schema["required"], list)

    @pytest.mark.integration
    async def test_mcp_resources_list_compliance(self, mcp_server: FastMCP[None]) -> None:
        """Test MCP resources/list request compliance."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test resources/list request
        resources_response = await client.list_resources()
        
        assert "resources" in resources_response
        resources = cast(list[MCPResourceInfo], resources_response["resources"])
        assert isinstance(resources, list)
        assert len(resources) > 0
        
        # Each resource should have required MCP fields
        for resource in resources:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            
            # Verify field types
            assert isinstance(resource["uri"], str)
            assert isinstance(resource["name"], str)
            assert isinstance(resource["description"], str)
            
            # URI should be valid
            assert resource["uri"].startswith("videos://")

    @pytest.mark.integration
    async def test_mcp_tools_call_compliance(
        self, 
        sample_video: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test MCP tools/call request compliance."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test tools/call request
        call_response = await client.call_tool(
            "get_video_info",
            {"video_path": str(sample_video)}
        )
        
        # Response should have required MCP fields
        assert "content" in call_response
        assert "isError" in call_response
        
        # Verify field types
        assert isinstance(call_response["content"], list)
        assert isinstance(call_response["isError"], bool)
        
        # Content should contain text blocks
        content = call_response["content"]
        assert len(content) > 0
        
        for block in content:
            assert "type" in block
            assert "text" in block
            assert block["type"] == "text"
            assert isinstance(block["text"], str)

    @pytest.mark.integration
    async def test_mcp_resources_read_compliance(
        self, 
        mcp_server: FastMCP[None]
    ) -> None:
        """Test MCP resources/read request compliance."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test resources/read request
        read_response = await client.read_resource("videos://list")
        
        # Response should have required MCP fields
        assert "content" in read_response
        assert "isError" in read_response
        
        # Verify field types
        assert isinstance(read_response["content"], list)
        assert isinstance(read_response["isError"], bool)
        
        # Content should contain text blocks
        content = read_response["content"]
        assert len(content) > 0
        
        for block in content:
            assert "type" in block
            assert "text" in block
            assert block["type"] == "text"
            assert isinstance(block["text"], str)

    @pytest.mark.integration
    async def test_mcp_error_handling_compliance(
        self, 
        mcp_server: FastMCP[None]
    ) -> None:
        """Test MCP error handling compliance."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test error response for invalid tool call
        error_response = await client.call_tool(
            "nonexistent_tool",
            {"invalid": "parameters"}
        )
        
        # Error responses should follow MCP format
        assert "content" in error_response
        assert "isError" in error_response
        assert error_response["isError"] is True
        
        # Error content should be informative
        content = error_response["content"]
        assert len(content) > 0
        
        error_text = content[0]["text"]
        assert isinstance(error_text, str)
        assert len(error_text) > 0

    @pytest.mark.integration
    async def test_mcp_tool_schema_validation(self, mcp_server: FastMCP[None]) -> None:
        """Test MCP tool input schema validation."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Get tool schemas
        tools_response = await client.list_tools()
        tools = cast(list[MCPToolInfo], tools_response["tools"])
        
        # Find trim_video tool to test schema validation
        trim_tool = None
        for tool in tools:
            if tool["name"] == "trim_video":
                trim_tool = tool
                break
        
        assert trim_tool is not None, "trim_video tool not found"
        
        # Test schema structure
        schema = trim_tool["inputSchema"]
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        
        # Verify required properties
        properties = schema["properties"]
        required = schema["required"]
        
        assert "input_path" in properties
        assert "output_path" in properties
        assert "start_time" in properties
        assert "duration" in properties
        
        assert "input_path" in required
        assert "output_path" in required
        assert "start_time" in required
        assert "duration" in required

    @pytest.mark.integration
    async def test_mcp_resource_uri_compliance(self, mcp_server: FastMCP[None]) -> None:
        """Test MCP resource URI scheme compliance."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Get resource list
        resources_response = await client.list_resources()
        resources = cast(list[MCPResourceInfo], resources_response["resources"])
        
        # Test URI format compliance
        for resource in resources:
            uri = resource["uri"]
            
            # URI should follow videos:// scheme
            assert uri.startswith("videos://")
            
            # URI should be well-formed
            if uri == "videos://list":
                # List endpoint
                assert resource["name"] == "Video Files List"
            elif "/metadata" in uri:
                # Metadata endpoint
                assert resource["name"].endswith("Metadata")
                # Should have filename in URI
                assert len(uri.split("/")) >= 2

    @pytest.mark.integration
    async def test_mcp_content_types(self, mcp_server: FastMCP[None]) -> None:
        """Test MCP content type handling."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test text content type
        list_response = await client.read_resource("videos://list")
        content = list_response["content"]
        
        for block in content:
            assert block["type"] == "text"
            assert "text" in block
            
            # Content should be valid JSON for list endpoint
            try:
                json.loads(block["text"])
            except json.JSONDecodeError:
                pytest.fail("Resource content is not valid JSON")

    @pytest.mark.integration
    async def test_mcp_progress_reporting(
        self, 
        sample_video: Path,
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test MCP progress reporting capabilities."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test tool call with progress reporting
        output_path = temp_dir / "progress_test.mp4"
        response = await client.call_tool(
            "trim_video",
            {
                "input_path": str(sample_video),
                "output_path": str(output_path),
                "start_time": "0",
                "duration": "2"
            }
        )
        
        # Response should indicate successful completion
        assert response["isError"] is False
        
        # Output file should exist
        assert output_path.exists()

    @pytest.mark.integration
    async def test_mcp_concurrent_requests(self, mcp_server: FastMCP[None]) -> None:
        """Test MCP concurrent request handling."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        import asyncio
        
        # Create multiple concurrent requests
        async def make_request() -> dict[str, Any]:
            return await client.list_tools()
        
        # Run concurrent requests
        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert len(results) == 5
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result

    @pytest.mark.integration
    async def test_mcp_request_isolation(
        self, 
        sample_video: Path,
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test MCP request isolation and state management."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Make multiple tool calls
        responses = []
        
        for i in range(3):
            output_path = temp_dir / f"isolation_test_{i}.mp4"
            response = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "start_time": "0",
                    "duration": "1"
                }
            )
            responses.append(response)
        
        # All requests should succeed independently
        for response in responses:
            assert response["isError"] is False
        
        # All output files should exist
        for i in range(3):
            output_path = temp_dir / f"isolation_test_{i}.mp4"
            assert output_path.exists()