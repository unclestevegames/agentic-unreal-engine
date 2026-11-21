#!/usr/bin/env python3
"""ue_mcp.py — shared CLI for Unreal's MCP server (official plugin, UE 5.8).

The one canonical way agents talk to the editor. Handles the JSON-RPC session
dance (initialize -> Mcp-Session-Id -> notifications/initialized), the
call_tool meta-tool wrapping, SSE responses, and base64 screenshot decoding.

This is the permanent, living interface, not a prototype: when MCP has a real
gap, extend this file (or add a standalone editor-Python script) directly rather
than working around it ad hoc.

Transport notes (learned the hard way — do not "simplify"):
  * The server only streams SSE bodies on KEEP-ALIVE connections; urllib's
    per-request Connection:close yields empty bodies. Hence http.client with
    a persistent connection.
  * SSE responses carry no Content-Length; read line-by-line and stop at the
    first complete JSON-RPC response event (read-to-EOF blocks ~15s until the
    server's keep-alive timeout).
  * Lines end \r\n.

Usage:
  python scripts/ue_mcp.py status
  python scripts/ue_mcp.py toolsets
  python scripts/ue_mcp.py describe <toolset_name>
  python scripts/ue_mcp.py call <toolset_name> <tool_name> [--args '<json>'] [--args-file <path>]
  python scripts/ue_mcp.py screenshot --out <file.png> [--asset </Game/Path>]

Options: --url (default http://127.0.0.1:8000/mcp), --timeout seconds (default 120).
Exit codes: 0 ok; 1 tool/server reported an error; 2 usage; 3 cannot reach server.

PowerShell callers: ALWAYS use --args-file, never inline --args '<json>' —
Windows PowerShell 5.1 strips the inner double quotes when passing the JSON to
a native process, producing a parse error. Write the file first, e.g.:
  Set-Content -Path $f -Value '{"ref":""}' -Encoding ascii
  python scripts\\ue_mcp.py call <toolset> <tool> --args-file $f
"""
import argparse
import base64
import http.client
import json
import re
import sys
import urllib.parse

DEFAULT_URL = "http://127.0.0.1:8000/mcp"


class McpError(Exception):
    pass


class McpSession:
    def __init__(self, url: str, timeout: float):
        parts = urllib.parse.urlsplit(url)
        self.host = parts.hostname or "127.0.0.1"
        self.port = parts.port or 80
        self.path = parts.path or "/mcp"
        self.timeout = timeout
        self.session_id = None
        self.protocol_version = None
        self._next_id = 0
        self._conn = None

    def _connection(self) -> http.client.HTTPConnection:
        if self._conn is None:
            self._conn = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
        return self._conn

    def _drop_connection(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except OSError:
                pass
            self._conn = None

    def _read_sse_response(self, resp) -> dict:
        """Incrementally read SSE; return the first event that is a JSON-RPC response."""
        current = []

        def flush():
            if not current:
                return None
            data = "\n".join(current)
            current.clear()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                return None
            if isinstance(msg, dict) and ("result" in msg or "error" in msg):
                return msg
            return None

        while True:
            raw = resp.readline()
            if not raw:
                msg = flush()
                if msg:
                    return msg
                raise McpError("SSE stream ended without a JSON-RPC response")
            line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            if line == "":
                msg = flush()
                if msg:
                    return msg
                continue
            if line.startswith("data:"):
                current.append(line[5:].lstrip())

    def _post(self, payload: dict, expect_response: bool) -> dict | None:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        if self.protocol_version:
            headers["MCP-Protocol-Version"] = self.protocol_version
        conn = self._connection()
        conn.request("POST", self.path, body=json.dumps(payload), headers=headers)
        resp = conn.getresponse()

        sid = resp.getheader("Mcp-Session-Id")
        if sid:
            self.session_id = sid
        ctype = resp.getheader("Content-Type") or ""

        if "text/event-stream" in ctype:
            try:
                msg = self._read_sse_response(resp)
            finally:
                # We stopped mid-stream; the connection can't be reused.
                self._drop_connection()
            return msg if expect_response else None

        body = resp.read().decode("utf-8", errors="replace")
        if not expect_response or not body.strip():
            return None
        return json.loads(body)

    def rpc(self, method: str, params: dict | None = None) -> dict:
        self._next_id += 1
        payload = {"jsonrpc": "2.0", "id": self._next_id, "method": method}
        if params is not None:
            payload["params"] = params
        msg = self._post(payload, expect_response=True)
        if msg is None:
            raise McpError(f"empty response to {method}")
        if "error" in msg:
            raise McpError(json.dumps(msg["error"], indent=2))
        return msg["result"]

    def notify(self, method: str) -> None:
        self._post({"jsonrpc": "2.0", "method": method}, expect_response=False)

    def connect(self) -> dict:
        info = self.rpc("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "ue_mcp.py", "version": "1.0"},
        })
        # Adopt the server's negotiated version for subsequent request headers.
        self.protocol_version = info.get("protocolVersion")
        self.notify("notifications/initialized")
        return info

    def tool_call(self, name: str, arguments: dict) -> dict:
        return self.rpc("tools/call", {"name": name, "arguments": arguments})


def content_items(result: dict) -> list:
    return result.get("content", []) if isinstance(result, dict) else []


def texts_of(result: dict) -> str:
    parts = []
    for item in content_items(result):
        if item.get("type") == "text":
            parts.append(item.get("text", ""))
    return "\n".join(parts)


def print_result(result: dict) -> int:
    """Pretty-print a tools/call result; return exit code (1 if isError)."""
    text = texts_of(result)
    # Tool outputs are often JSON-in-text; pretty-print when they parse.
    try:
        print(json.dumps(json.loads(text), indent=2))
    except (json.JSONDecodeError, TypeError):
        print(text)
    if result.get("isError"):
        print("(tool reported isError=true)", file=sys.stderr)
        return 1
    return 0


def extract_png(result: dict) -> bytes:
    """Find base64 PNG data in a tool result (image content item, or b64 in text)."""
    for item in content_items(result):
        if item.get("type") == "image" and item.get("data"):
            return base64.b64decode(item["data"])
    text = texts_of(result)
    try:
        payload = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        payload = None

    def find_b64(node):
        if isinstance(node, str) and re.fullmatch(r"[A-Za-z0-9+/=\s]+", node):
            try:
                if base64.b64decode(node).startswith(b"\x89PNG\r\n\x1a\n"):
                    return node
            except ValueError:
                pass
        if isinstance(node, dict):
            for v in node.values():
                found = find_b64(v)
                if found:
                    return found
        if isinstance(node, list):
            for v in node:
                found = find_b64(v)
                if found:
                    return found
        return None

    blob = find_b64(payload) if payload is not None else None
    if blob is None:
        raise McpError("no image data found in tool result; raw text follows:\n" + text[:2000])
    return base64.b64decode(blob)


def main() -> int:
    # Windows consoles often default to cp1252; tool output is UTF-8-ish.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="ue_mcp.py", add_help=True)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=120.0)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status")
    sub.add_parser("toolsets")
    p_desc = sub.add_parser("describe")
    p_desc.add_argument("toolset")
    p_call = sub.add_parser("call")
    p_call.add_argument("toolset")
    p_call.add_argument("tool")
    p_call.add_argument("--args", default=None, help="JSON object of tool arguments")
    p_call.add_argument("--args-file", default=None, help="path to a JSON file of tool arguments")
    p_shot = sub.add_parser("screenshot")
    p_shot.add_argument("--out", required=True, help="output .png path")
    p_shot.add_argument("--asset", default=None,
                        help="capture this asset (/Game/...) instead of the editor viewport")

    opts = parser.parse_args()
    session = McpSession(opts.url, opts.timeout)

    try:
        info = session.connect()
    except (OSError, McpError) as e:
        print(f"cannot reach MCP server at {opts.url}: {e}", file=sys.stderr)
        print("Is the editor running? Start it with scripts\\ue-editor.ps1 start -Project <uproject>",
              file=sys.stderr)
        return 3

    if opts.cmd == "status":
        server = info.get("serverInfo", {})
        print(f"OK {opts.url} - {server.get('name') or 'UE MCP'} {server.get('version', '')}"
              f" (protocol {session.protocol_version}, session {session.session_id})")
        return 0

    try:
        if opts.cmd == "toolsets":
            return print_result(session.tool_call("list_toolsets", {}))

        if opts.cmd == "describe":
            return print_result(session.tool_call("describe_toolset",
                                                  {"toolset_name": opts.toolset}))

        if opts.cmd == "call":
            if opts.args and opts.args_file:
                print("use --args OR --args-file, not both", file=sys.stderr)
                return 2
            if opts.args_file:
                with open(opts.args_file, encoding="utf-8") as f:
                    arguments = json.load(f)
            else:
                arguments = json.loads(opts.args) if opts.args else {}
            return print_result(session.tool_call("call_tool", {
                "toolset_name": opts.toolset,
                "tool_name": opts.tool,
                "arguments": arguments,
            }))

        if opts.cmd == "screenshot":
            if opts.asset:
                tool, arguments = "CaptureAssetImage", {"AssetPath": opts.asset}
            else:
                tool, arguments = "CaptureEditorImage", {}
            result = session.tool_call("call_tool", {
                "toolset_name": "EditorToolset.EditorAppToolset",
                "tool_name": tool,
                "arguments": arguments,
            })
            if result.get("isError"):
                print(texts_of(result), file=sys.stderr)
                return 1
            png = extract_png(result)
            with open(opts.out, "wb") as f:
                f.write(png)
            print(f"wrote {opts.out} ({len(png)} bytes)")
            return 0
    except McpError as e:
        print(f"MCP error: {e}", file=sys.stderr)
        return 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
