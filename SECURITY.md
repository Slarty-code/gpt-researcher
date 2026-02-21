# Security

This document summarizes GPT-Researcher’s security posture and points to detailed hardening and residual risk.

## Security planning and hardening

A structured **security planning report** is in the repo: [`security planning report.txt`](security%20planning%20report.txt). It defines threat model, trust boundaries, and minimal safe integration. The following hardening has been implemented against that report:

- **Prompt injection (report §4.1, §7):** Strict system/user prompt hierarchy, non-overridable safety policy in the system prompt, pattern-based injection detection (redaction) on user/context content, and an optional LLM reflection step before MCP tool execution.
- **Trust boundaries (report §3):** Context sources are tagged with a trust level (e.g. untrusted) and formatted so the model sees them as untrusted data.
- **RAG/corpus poisoning (report §4.4):** Content is sanitized (injection-pattern scan and normalization) before being loaded into the vector store.
- **MCP tool policy (report §4.2, §9):** MCP is opt-in; when enabled, tools are filtered by a denylist (and optional allowlist). High/critical tools require human-in-the-loop and are skipped if not approved. See [MCP Security and Tool Policy](docs/docs/gpt-researcher/mcp-server/security.md).
- **Human over-trust (report §4.5):** UI disclaimers state that reports are generated from web and uploaded sources and may contain errors or source bias; users are asked to verify critical claims.
- **Data exfiltration (report §4.3, §5.5):** API keys and secrets are not interpolated into prompts or tool inputs. MCP server env config is filtered to avoid passing secret-like variables to servers. All MCP tool invocations are logged for audit.

File upload and deletion are already hardened (path traversal protection, secure filename, validation) and covered by tests in `tests/test_security_fix.py`.

## Residual risk (report §10)

Even with these controls, residual risks remain:

- **Novel prompt injection methods** that evade pattern-based filters.
- **Model hallucinated policy reasoning** (e.g. incorrectly concluding an instruction is safe).
- **Social engineering via generated content** (reports that persuade users to take unsafe actions).
- **Insider misuse** (privileged users enabling unsafe MCP servers or disabling safeguards).
- **Undetected data poisoning** (content that influences outputs without triggering injection patterns).

Agentic systems are probabilistic; security should assume failure modes and layer defenses (infrastructure, tool restriction, prompt governance, human training, audit).

## Reporting vulnerabilities

If you believe you have found a security vulnerability, please report it in a responsible way (e.g. via the project’s security policy or maintainer contact rather than in a public issue).
