"""
MCP tool policy: allowlist/denylist for minimal safe integration (report §4.2, §9).

Allow: web search, structured research, read-only document retrieval.
Disallow: shell execution, file writes, git operations, Docker control, arbitrary HTTP POST.
"""
import logging
from typing import List, Any

logger = logging.getLogger(__name__)

# Default denylist substrings (case-insensitive) for tool name + description.
# Report §9: disallow shell, file writes, git, Docker, arbitrary POST.
DEFAULT_DENIED_PATTERNS = [
    "shell", "exec", "run_command", "execute", "subprocess", "eval",
    "write_file", "write file", "file_write", "save_file", "create_file",
    "git_push", "git push", "git_write", "git_commit",
    "docker", "container_run", "run_container",
    "http_post", "post_request", "arbitrary post", "fetch_post",
    "read_file", "read env", "environment", "getenv", "env_var",
]

# Optional allowlist: if set, only tools whose name matches one of these (regex or substring) are allowed.
# When empty, only the denylist is applied.
DEFAULT_ALLOWED_PATTERNS = []  # Empty = no allowlist filter, only denylist


def filter_tools_by_policy(
    tools: List[Any],
    denied_patterns: List[str] | None = None,
    allowed_patterns: List[str] | None = None,
) -> List[Any]:
    """
    Return only tools that pass the policy (report §9 minimal safe integration).

    - If allowed_patterns is non-empty: tool name must match at least one allowed pattern.
    - Tool is excluded if name or description matches any denied_patterns (case-insensitive).
    """
    if not tools:
        return []
    denied = denied_patterns if denied_patterns is not None else DEFAULT_DENIED_PATTERNS
    allowed = allowed_patterns if allowed_patterns is not None else DEFAULT_ALLOWED_PATTERNS

    result = []
    for tool in tools:
        name = getattr(tool, "name", "") or ""
        desc = (getattr(tool, "description", None) or "") or ""
        combined = f"{name} {desc}".lower()

        # Denylist: exclude if any denied pattern matches
        if any(p.lower() in combined for p in denied):
            logger.debug(f"MCP tool policy: denied tool '{name}' (matches denylist)")
            continue

        # Allowlist: if configured, include only if name matches an allowed pattern (substring, case-insensitive)
        if allowed:
            if not any(p.lower() in name.lower() for p in allowed):
                logger.debug(f"MCP tool policy: excluded tool '{name}' (not in allowlist)")
                continue

        result.append(tool)
    return result


def classify_tool_risk(tool: Any) -> str:
    """
    Classify tool risk for human-in-the-loop (report §6.1).
    Returns "low", "medium", "high", or "critical".
    """
    name = (getattr(tool, "name", "") or "").lower()
    desc = (getattr(tool, "description", None) or "").lower()
    combined = f"{name} {desc}"

    if any(x in combined for x in ["shell", "exec", "run_command", "docker", "git_push", "write_file", "post_request"]):
        return "critical"
    if any(x in combined for x in ["write", "git", "file_write", "http_post"]):
        return "high"
    if any(x in combined for x in ["read_file", "read env", "getenv", "environment"]):
        return "medium"
    return "low"
