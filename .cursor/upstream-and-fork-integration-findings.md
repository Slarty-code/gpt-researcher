# Upstream and Fork Integration Review — Findings

Generated from the [Upstream and fork review](.cursor/plans/upstream_and_fork_review_d1c5a7b2.plan.md) workflow. Branch: `feature/Slarty-next`. Upstream: `assafelovic/gpt-researcher` (master).

---

## 1. Upstream comparison (after `git fetch upstream`)

- **Commits behind upstream/master:** 41
- **Merge-base with upstream:** `e96df079` ("updated docs link for modifying llms")

### Commits on upstream/master not in feature/Slarty-next (newest first)

| Commit     | Description |
|-----------|-------------|
| 10dede64  | update skills.sh download option |
| 75fa22b7  | refactored skills directory structure |
| 01c39767  | refactored skills to fit best standards |
| c99f25c8  | updated docs with nano banan |
| 81690a9b  | added docs for image generation and ai development |
| 09c76605  | Merge #1608 feature/image_generation |
| a367c96a  | fixed docs |
| 50341094  | removed docker push entirely |
| 75eb6b6e  | added skills for further development of gptr |
| 6e12b998  | updated docs |
| 3bcf50a7  | improve logic architecture of generating images in workflow |
| 433857ac  | added image generation with nano banana |
| b66b7c0c  | Merge #1599 feat/langsmith-integration |
| c8d1f3da  | Merge #1604 add-aggregated-summary-to-quick-search |
| c53e2064  | Add aggregated summary flag to quick_search |
| b1407de2  | feat: enable LangSmith tracing for enhanced observability |
| 50383b43  | Merge #1596 Remove hardcoded authentication token |
| 0a6d6d54  | Remove hardcoded authentication token |
| 0936a029  | Merge #1594 fix/reports-persistence |
| 8dc7df7d  | Merge #1593 feat/websocket-chat-implementation |
| e902ebd7  | Merge #1590 feature/refactor (ECR/GHA Terraform) |
| 751d772a  | Merge #1589 claude/fix-automated-checks |
| 3fe73dbf  | Merge #1595 fix/cors-origins |
| e514a870  | Fix invalid CORS defaults with credentialed requests |
| a2651961  | Persist report history for /api/reports endpoints |
| 410d3bad  | feat: WebSocket chat command handling & make Tavily optional |
| db7f17ee  | refactor: ECR and GitHub Actions Terraform setup |
| ecf6a37b  | docs: docstrings for memory and context compression |
| a3b9b3bd  | docs: comprehensive docstrings for coverage |
| 2a94c18f  | Merge #1573 fix-markdown-pdf-css-path |
| eab7c798  | Merge #1568 feature/multiagents-write-to-file-utf8 |
| 082a842b  | Merge #1567 feature/fix-multiagents-docx-path-v2 |
| 8b13cfbf  | fix: resolve markdown pdf css path from backend module |
| 17778d1c  | Merge #1565 fix/openrouter-timeout |
| 6c579642  | Merge #1564 feature/domain-filter-component |
| d749d2d0  | Merge #1562 improve/error-handling |
| 86495e24  | chore: align multi_agents write_to_file with backend UTF-8 |
| a5351306  | fix: avoid double .docx extension in multi_agents write_md_to_word |
| 3278d903  | fix: Add request_timeout to OpenRouter provider |
| a417aca0  | refactor: extract domain filter UI into DomainFilter component |
| 7d26af7f  | Improve error handling with better messages and logging |

---

## 2. GitHub Releases — integration candidates

**Releases URL:** https://github.com/assafelovic/gpt-researcher/releases

### v3.4.1 (Latest — 21 Feb 2026)

- fix: handle list context in deep research to prevent AttributeError (#1637)
- Attempt to load config path from env var if no path provided (#1630)
- feat: Forge LLM provider support (#1626)
- Add openrouter embeddings support (#1620)
- add bocha search tool (#1618)
- Update server_utils.py — fixed file name via hash (#1611)

*Note: v3.4.1 may include commits not yet in upstream/master at time of fetch; confirm with `git log upstream/master -5` or tag.*

### v3.4.0 (29 Jan 2026)

- **Inline image generation** (Gemini, configurable; IMAGE_GENERATION_*)
- **LangSmith integration** (LANGCHAIN_TRACING_V2, observability)
- **Claude Code skills** (`.claude/skills/`, REFERENCE.md, SKILL.md)
- Aggregated summary flag for quick_search (#1604)
- Docs: AI-Assisted Development, Image Generation

### v3.3.9 (25 Jan 2026)

- Remove hardcoded authentication token (#1596)
- Persist /api/reports history to local JSON (#1594)
- WebSocket chat command handling & make Tavily optional (#1593)
- ECR/GitHub Actions Terraform refactor (#1590)
- Docstrings for memory and context compression (#1589)
- Fix CORS defaults when allow_credentials=true (#1595)

### v.3.3.8 (14 Dec 2025)

- fix: markdown→PDF CSS path from backend (#1573)
- multi_agents write_to_file UTF-8 alignment (#1568)
- fix: double .docx extension in write_md_to_word (#1567)
- fix: OpenRouter request_timeout (#1565)
- Domain filter UI → DomainFilter component (#1564)
- Improved error handling and logging (#1562)
- Railway: missing LangChain deps (#1555)
- CLI output format control flags (#1553)
- Firecrawl scraper AttributeError fix (#1552)
- Configurable rate limiting for scraper backends (#1550)

---

## 3. Open pull requests (upstream) — worth watching

**PRs URL:** https://github.com/assafelovic/gpt-researcher/pulls (30 open)

Notable open PRs that may be worth integrating or cherry-picking:

| PR    | Title / theme |
|-------|-------------------------------|
| #1623 | fix: Read all pages in PyMuPDFScraper (not just first page) |
| #1616 | Update websockets requirement (dependabot) |
| #1615 | Update langgraph requirement (dependabot) |
| #1614 | Update json-repair requirement (dependabot) |
| #1613 | Update json5 requirement (dependabot) |
| #1612 | Bump Docker python to 3.14-slim-bookworm (dependabot) |
| #1610 | Add custom writing instructions for report generation |
| #1607 | fix potential data parsing issue in web scraping |
| #1588 | fix: properly handle WebSocketDisconnect in handle_websocket_communication |
| #1584 | Add custom prompts and language parameter |
| #1576 | fix: Tavily search longer than 400 characters (#1263) |
| #1558 | Add query_domains support to search retrievers |
| #1557 | Enhanced MCP server with security fixes and improvements |
| #1535 | feat: add plan manager and budgeting layer |
| #1337 | Docling integration |
| #1007 | Massive refactor: "black box" retrievers (assafelovic) |

---

## 4. Forks

- **Network:** https://github.com/assafelovic/gpt-researcher/network (shows ~50 most recently pushed forks; interactive graph).
- **Fork count:** ~3.4k. Systematic review of all forks is not practical.
- **Suggested approach:** Use the network page and “Recently updated” / stars to pick a small set of high-signal forks; add as remotes and run `git log feature/Slarty-next..<fork>/<branch> --oneline` for branches you care about.

---

## 5. Integration priority summary

### High priority (bugfixes / stability / security)

- **OpenRouter timeout** — #1565 (request_timeout to prevent hangs) — already in the 41 commits.
- **Firecrawl AttributeError** — #1552 — already in the 41 commits.
- **Markdown→PDF CSS path** — #1573 — resolve path from backend.
- **CORS with credentials** — #1595 — fix invalid CORS defaults when allow_credentials=true.
- **multi_agents .docx / UTF-8** — #1567, #1568 — double .docx extension and UTF-8 alignment.
- **Deep research list context AttributeError** — in v3.4.1 (#1637).
- **Remove hardcoded auth token** — #1596.
- **WebSocket disconnect handling** — open PR #1588 (consider cherry-pick when merged or from fork).

### Medium priority (features / quality, lower conflict risk with owui)

- **Scraper rate limiting** — #1550 — configurable rate limiting for scrapers.
- **CLI output format flags** — #1553 — selective report generation.
- **Error handling and logging** — #1562.
- **Domain filter component** — #1564 — extract DomainFilter UI (assess overlap with owui).
- **Report persistence** — #1594 — /api/reports history to local JSON.
- **LangSmith tracing** — #1599 — optional observability (LANGCHAIN_TRACING_V2).
- **Aggregated summary for quick_search** — #1604.
- **Config path from env** — v3.4.1 #1630.
- **Open PRs:** PyMuPDF all pages (#1623), Tavily 400-char fix (#1576), query_domains for retrievers (#1558), MCP security (#1557).

### Lower / case-by-case (assess vs feature/Slarty-next)

- **Image generation** — #1608 — Gemini-based; new workflow and config.
- **WebSocket chat / Tavily optional** — #1593 — may overlap with owui flows.
- **Terraform / ECR / GHA** — #1590 — infra only.
- **Skills / docs** — skills directory and docs; low code conflict.
- **Custom writing instructions / prompts** — open PRs #1610, #1584 — align with your report-quality goals if desired.

---

## 6. Suggested next steps

1. **Merge or rebase upstream into feature/Slarty-next** to pull in the 41 commits (or a range up to a chosen tag, e.g. `v.3.3.8` or `v3.4.0`), then resolve conflicts.
2. **Cherry-pick** any high-priority fixes if you prefer not to merge the full set (e.g. OpenRouter timeout, Firecrawl, PDF CSS, CORS, .docx/UTF-8).
3. **Watch or apply** open PRs #1623 (PyMuPDF), #1576 (Tavily), #1588 (WebSocket disconnect), #1558 (query_domains), #1557 (MCP) when merged or from author branches.
4. **Re-run this workflow** periodically: `git fetch upstream && git fetch upstream --tags`, then `git log feature/Slarty-next..upstream/master --oneline` and re-check [Releases](https://github.com/assafelovic/gpt-researcher/releases) and [Pull requests](https://github.com/assafelovic/gpt-researcher/pulls).
