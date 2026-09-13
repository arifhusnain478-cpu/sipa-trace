import asyncio
import json
from mcp.server.mcpserver import MCPServer

from sipa_trace.chain import TraceLog
from sipa_trace.pipeline import traced
from sipa_trace.risk import ActionProfile

# 1. Initialize trace log destination
trace_log = TraceLog("trace.jsonl")

# 2. Initialize MCPServer Gateway
mcp = MCPServer("Production-Infra-Gateway")
 
# 3. Wire @traced around tool handlers
@mcp.tool()
@traced(
    trace_log,
    stage="tool_execution",
    action_type="infrastructure_query",
    profile=ActionProfile()
)
async def query_cluster_health(cluster_id: str) -> str:
    """Queries health telemetry for an infrastructure cluster."""
    await asyncio.sleep(0.05)
    return json.dumps({
        "cluster_id": cluster_id,
        "status": "healthy",
        "nodes_online": 4
    })

@mcp.tool()
@traced(
    trace_log,
    stage="tool_execution",
    action_type="credential_access",
    profile=ActionProfile(external_network_call=True, touches_credentials=True)
)
async def rotate_service_token(service_name: str) -> str:
    """Rotates a production service access token."""
    await asyncio.sleep(0.08)
    return json.dumps({
        "service_name": service_name,
        "status": "rotated"
    })

if __name__ == "__main__":
    print("[+] Running MCP Server with @traced active...")
    print("[+] Output trace file will be written to: trace.jsonl")
    
    # Wrap the run command to catch Ctrl + C gracefully
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\n[+] Server stopped cleanly by user.")