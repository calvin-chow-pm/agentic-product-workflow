"""Small stdio MCP adapter; no third-party dependencies or generic file tools."""
import json
import sys

from .core import Capability


TOOLS = [
    {"name": "read_workspace", "description": "Read only exported context, feedback, proposals, and aggregate insight. No raw dataset access.", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "request_analysis", "description": "Write a fixed aggregate link_usage request to _outbox; trusted worker processes it separately.", "inputSchema": {"type": "object", "properties": {"request_id": {"type": "string"}, "operation": {"type": "string", "enum": ["link_usage"]}}, "additionalProperties": False}},
    {"name": "check_inbox", "description": "Read the response for a specific request, or report pending.", "inputSchema": {"type": "object", "properties": {"request_id": {"type": "string"}}, "additionalProperties": False}},
    {"name": "submit_proposal", "description": "Capture a role's evidence-based proposal with observations, hypotheses, alternatives and recommendation.", "inputSchema": {"type": "object", "properties": {"role": {"type": "string", "enum": ["strategy", "challenger", "design", "engineering", "qa"]}, "value": {"type": "object"}}, "required": ["role", "value"], "additionalProperties": False}},
    {"name": "stage_learning", "description": "Propose a lesson outside authoritative context. Cannot approve or sync it.", "inputSchema": {"type": "object", "properties": {"lesson": {"type": "string"}}, "required": ["lesson"], "additionalProperties": False}},
]


def serve_mcp(demo):
    capability = Capability(demo)
    for line in sys.stdin:
        try:
            message = json.loads(line)
            if "id" not in message:
                continue
            method = message.get("method")
            if method == "initialize":
                result = {"protocolVersion": message.get("params", {}).get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}}, "serverInfo": {"name": "winzip-reconstruction-workspace", "version": "1.0.0"}}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                params = message.get("params", {})
                try:
                    value = capability.call(params["name"], params.get("arguments", {}))
                    result = {"content": [{"type": "text", "text": json.dumps(value)}]}
                except (ValueError, FileNotFoundError, KeyError) as exc:
                    result = {"isError": True, "content": [{"type": "text", "text": str(exc)}]}
            elif method == "ping":
                result = {}
            else:
                print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32601, "message": "Method unavailable"}}), flush=True)
                continue
            print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}), flush=True)
        except (ValueError, KeyError) as exc:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}), flush=True)
