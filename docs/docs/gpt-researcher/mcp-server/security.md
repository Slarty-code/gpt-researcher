---
sidebar_position: 4
---

# MCP Security and Tool Policy

Enabling MCP expands the attack surface: the retriever can run whatever tools the configured servers expose. This page describes the **minimal safe integration** model and how to lock down which tools are allowed.

## Default: Research-Only Mode

- **Research-only mode is the default.** MCP is **opt-in**: it is only active when `mcp_enabled` is true and `mcp_configs` are provided (e.g. from the frontend or API).
- When MCP is disabled, no external tool servers are used; only built-in retrievers (e.g. Tavily, Brave) and report generation run.

## Minimal Safe Integration (Report §9)

When you enable MCP, the following policy is applied:

- **Allow:** Web search, structured research, read-only document retrieval.
- **Disallow:** Shell execution, file writes, git operations, Docker control, arbitrary HTTP POST, reading environment variables or arbitrary files.

Tool filtering is implemented in `gpt_researcher/mcp/tool_policy.py`. After loading tools from all configured MCP servers, the retriever applies a **denylist** (and optional **allowlist**) so only permitted tools are available to the LLM.

## Configuration

You can tighten or relax the policy via config (e.g. `config.json` or environment):

| Option | Description |
|--------|-------------|
| `MCP_DENIED_TOOL_PATTERNS` | List of substrings (case-insensitive) matched against tool **name** and **description**. Any tool matching one of these is excluded. Default: internal list (shell, exec, write_file, git, docker, http_post, read_file, getenv, etc.). Set to `[]` to use the internal default. |
| `MCP_ALLOWED_TOOLS` | Optional **allowlist**. If non-empty, only tools whose name contains one of these substrings are allowed. Empty = no allowlist; only the denylist is applied. |

Example: to allow only tools whose name contains `search` or `fetch`:

```json
{
  "MCP_ALLOWED_TOOLS": ["search", "fetch"]
}
```

## Audit

All MCP tool invocations are logged (tool name and, at debug level, arguments). Ensure logs are retained and not modifiable by the application for auditability.

## Recommendation

For regulated or high-assurance environments, keep MCP disabled and use research-only mode. If you enable MCP, use trusted server configs and consider setting `MCP_ALLOWED_TOOLS` to a narrow list of tool names you intend to use.

## Residual Risk (Section 10)

Even with the above controls, residual risks remain:

- **Novel prompt injection methods** that evade pattern-based filters.
- **Model hallucinated policy reasoning** (e.g. incorrectly concluding an instruction is safe).
- **Social engineering via generated content** (reports that persuade users to take unsafe actions).
- **Insider misuse** (privileged users enabling unsafe MCP servers or disabling safeguards).
- **Undetected data poisoning** (content that influences outputs without triggering injection patterns).

Agentic systems are probabilistic; security should assume failure modes and layer defenses (infrastructure, tool restriction, prompt governance, human training, audit).
