# Revisión diff — timeouts MCP

## 1. Estado Git

 M mcp_server/server.py
 M mcp_server/tools.py
?? docs/agent_queue/inbox/20260508_164958_f34d0ff4.json
?? docs/agent_queue/inbox/20260508_164958_f34d0ff4.md
?? docs/agent_queue/inbox/20260508_shell_timeout_fix_5112.json
?? docs/agent_queue/inbox/20260508_shell_timeout_fix_5112.md
?? docs/agent_queue/inbox/20260508_shell_timeout_fix_6175.json
?? docs/agent_queue/inbox/20260508_shell_timeout_fix_6175.md
?? docs/agent_queue/inbox/20260508_shell_timeout_fix_7466.json
?? docs/agent_queue/inbox/20260508_shell_timeout_fix_7466.md
?? docs/agent_runs/20260508_164958_f34d0ff4/
?? docs/agent_runs/20260508_shell_timeout_fix_5112/
?? docs/agent_runs/20260508_shell_timeout_fix_6175/
?? docs/agent_runs/20260508_shell_timeout_fix_7466/


## 2. Diff stat

 mcp_server/server.py |  6 +++++-
 mcp_server/tools.py  | 22 +++++++++++++++++++---
 2 files changed, 24 insertions(+), 4 deletions(-)


## 3. Diff mcp_server/server.py

diff --git a/mcp_server/server.py b/mcp_server/server.py
index d0f978a..d5c7726 100644
--- a/mcp_server/server.py
+++ b/mcp_server/server.py
@@ -59,11 +59,15 @@ def log(message: str) -> None:
 
 
 def as_tool_content(data: Any) -> dict[str, Any]:
+    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
+    limit = 32768
+    if len(raw) > limit:
+        raw = raw[:limit] + f"\n...[truncated: {len(raw)} chars total]"
     return {
         "content": [
             {
                 "type": "text",
-                "text": json.dumps(data, ensure_ascii=False, indent=2),
+                "text": raw,
             }
         ],
         "isError": bool(isinstance(data, dict) and data.get("ok") is False),


## 4. Diff mcp_server/tools.py

diff --git a/mcp_server/tools.py b/mcp_server/tools.py
index 10eca62..1488eee 100644
--- a/mcp_server/tools.py
+++ b/mcp_server/tools.py
@@ -39,7 +39,9 @@ ALLOWED_TOOLS = {
 }
 
 
-def _run_python_script(args: list[str], timeout: int = 180) -> dict[str, Any]:
+def _run_python_script(args: list[str], timeout: int = 180, max_output_chars: int = 24576) -> dict[str, Any]:
+    import time as _time
+    start = _time.perf_counter()
     completed = subprocess.run(
         [sys.executable, *args],
         cwd=ROOT,
@@ -49,11 +51,25 @@ def _run_python_script(args: list[str], timeout: int = 180) -> dict[str, Any]:
         errors="replace",
         timeout=timeout,
     )
+    elapsed_ms = int((_time.perf_counter() - start) * 1000)
+
+    def _truncate(text: str, limit: int) -> str:
+        if len(text) <= limit:
+            return text
+        return text[:limit] + f"\n... [truncated: {len(text)} chars total]"
+
+    stdout_raw = completed.stdout or ""
+    stderr_raw = completed.stderr or ""
 
     return {
         "returncode": completed.returncode,
-        "stdout": completed.stdout,
-        "stderr": completed.stderr,
+        "stdout": _truncate(stdout_raw, max_output_chars),
+        "stderr": _truncate(stderr_raw, max_output_chars),
+        "stdout_bytes": len(stdout_raw.encode("utf-8", errors="replace")),
+        "stderr_bytes": len(stderr_raw.encode("utf-8", errors="replace")),
+        "stdout_truncated": len(stdout_raw) > max_output_chars,
+        "stderr_truncated": len(stderr_raw) > max_output_chars,
+        "elapsed_ms": elapsed_ms,
         "ok": completed.returncode == 0,
     }
 

