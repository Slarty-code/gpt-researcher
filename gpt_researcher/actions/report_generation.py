import asyncio
from typing import List, Dict, Any, Union
from ..config.config import Config
from ..utils.llm import create_chat_completion
from ..utils.logger import get_formatted_logger
from ..prompts import PromptFamily, get_prompt_by_report_type
from ..utils.enum import Tone

logger = get_formatted_logger()


def format_context_for_report(context: Union[str, List[Dict[str, Any]]]) -> str:
    """
    Format context for the report prompt. If context is a list of source dicts,
    produce a string with clear source labels and citation hints for RAG (corpus) sources.
    """
    if isinstance(context, str):
        return context
    if not isinstance(context, list):
        return str(context)
    parts = []
    for i, item in enumerate(context):
        if not isinstance(item, dict):
            parts.append(str(item))
            continue
        body = item.get("body", item.get("raw_content", ""))
        href = item.get("href", "")
        source_type = item.get("source_type", "web")
        if source_type == "rag":
            doc_title = item.get("doc_title", "Corpus")
            location = item.get("location", "")
            cite_hint = f" [Cite as: [Source: {doc_title}, {location}]]"
            parts.append(f"--- Corpus source{cite_hint} ---\n{body}")
        else:
            parts.append(f"--- Web source: {href} ---\n{body}")
    return "\n\n".join(parts)


async def write_report_introduction(
    query: str,
    context: str,
    agent_role_prompt: str,
    config: Config,
    websocket=None,
    cost_callback: callable = None,
    prompt_family: type[PromptFamily] | PromptFamily = PromptFamily,
    **kwargs
) -> str:
    """
    Generate an introduction for the report.

    Args:
        query (str): The research query.
        context (str): Context for the report.
        role (str): The role of the agent.
        config (Config): Configuration object.
        websocket: WebSocket connection for streaming output.
        cost_callback (callable, optional): Callback for calculating LLM costs.
        prompt_family: Family of prompts

    Returns:
        str: The generated introduction.
    """
    try:
        introduction = await create_chat_completion(
            model=config.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{agent_role_prompt}"},
                {"role": "user", "content": prompt_family.generate_report_introduction(
                    question=query,
                    research_summary=context,
                    language=config.language
                )},
            ],
            temperature=0.25,
            llm_provider=config.smart_llm_provider,
            stream=True,
            websocket=websocket,
            max_tokens=config.smart_token_limit,
            llm_kwargs=config.llm_kwargs,
            cost_callback=cost_callback,
            **kwargs
        )
        return introduction
    except Exception as e:
        logger.error(f"Error in generating report introduction: {e}")
    return ""


async def write_conclusion(
    query: str,
    context: str,
    agent_role_prompt: str,
    config: Config,
    websocket=None,
    cost_callback: callable = None,
    prompt_family: type[PromptFamily] | PromptFamily = PromptFamily,
    **kwargs
) -> str:
    """
    Write a conclusion for the report.

    Args:
        query (str): The research query.
        context (str): Context for the report.
        role (str): The role of the agent.
        config (Config): Configuration object.
        websocket: WebSocket connection for streaming output.
        cost_callback (callable, optional): Callback for calculating LLM costs.
        prompt_family: Family of prompts

    Returns:
        str: The generated conclusion.
    """
    try:
        conclusion = await create_chat_completion(
            model=config.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{agent_role_prompt}"},
                {
                    "role": "user",
                    "content": prompt_family.generate_report_conclusion(query=query,
                                                                        report_content=context,
                                                                        language=config.language),
                },
            ],
            temperature=0.25,
            llm_provider=config.smart_llm_provider,
            stream=True,
            websocket=websocket,
            max_tokens=config.smart_token_limit,
            llm_kwargs=config.llm_kwargs,
            cost_callback=cost_callback,
            **kwargs
        )
        return conclusion
    except Exception as e:
        logger.error(f"Error in writing conclusion: {e}")
    return ""


async def summarize_url(
    url: str,
    content: str,
    role: str,
    config: Config,
    websocket=None,
    cost_callback: callable = None,
    **kwargs
) -> str:
    """
    Summarize the content of a URL.

    Args:
        url (str): The URL to summarize.
        content (str): The content of the URL.
        role (str): The role of the agent.
        config (Config): Configuration object.
        websocket: WebSocket connection for streaming output.
        cost_callback (callable, optional): Callback for calculating LLM costs.

    Returns:
        str: The summarized content.
    """
    try:
        summary = await create_chat_completion(
            model=config.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{role}"},
                {"role": "user", "content": f"Summarize the following content from {url}:\n\n{content}"},
            ],
            temperature=0.25,
            llm_provider=config.smart_llm_provider,
            stream=True,
            websocket=websocket,
            max_tokens=config.smart_token_limit,
            llm_kwargs=config.llm_kwargs,
            cost_callback=cost_callback,
            **kwargs
        )
        return summary
    except Exception as e:
        logger.error(f"Error in summarizing URL: {e}")
    return ""


async def generate_draft_section_titles(
    query: str,
    current_subtopic: str,
    context: str,
    role: str,
    config: Config,
    websocket=None,
    cost_callback: callable = None,
    prompt_family: type[PromptFamily] | PromptFamily = PromptFamily,
    **kwargs
) -> List[str]:
    """
    Generate draft section titles for the report.

    Args:
        query (str): The research query.
        context (str): Context for the report.
        role (str): The role of the agent.
        config (Config): Configuration object.
        websocket: WebSocket connection for streaming output.
        cost_callback (callable, optional): Callback for calculating LLM costs.
        prompt_family: Family of prompts

    Returns:
        List[str]: A list of generated section titles.
    """
    try:
        section_titles = await create_chat_completion(
            model=config.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{role}"},
                {"role": "user", "content": prompt_family.generate_draft_titles_prompt(
                    current_subtopic, query, context)},
            ],
            temperature=0.25,
            llm_provider=config.smart_llm_provider,
            stream=True,
            websocket=None,
            max_tokens=config.smart_token_limit,
            llm_kwargs=config.llm_kwargs,
            cost_callback=cost_callback,
            **kwargs
        )
        return section_titles.split("\n")
    except Exception as e:
        logger.error(f"Error in generating draft section titles: {e}")
    return []


def _extract_allowed_urls_from_context(context) -> List[str]:
    """Extract list of allowed URLs from context when it is a list of source dicts."""
    urls = []
    if not isinstance(context, list):
        return urls
    for item in context:
        if isinstance(item, dict) and item.get("href"):
            urls.append(item["href"].strip())
    return list(dict.fromkeys(urls))


async def improve_report_citations(
    report: str,
    allowed_urls: List[str],
    config: Config,
    report_format: str = "apa",
    websocket=None,
    cost_callback: callable = None,
    **kwargs
) -> str:
    """
    Post-process the report to improve citations: ensure markdown link format
    ([in-text citation](url)), use only allowed URLs, and fix broken or invalid citations.
    """
    if not report or not allowed_urls:
        return report
    allowed_list = "\n".join(f"- {u}" for u in allowed_urls[:80])
    prompt = f"""You are a citation editor. Given a research report and the list of allowed source URLs, improve the report's citations as follows:

1. Keep the report content and structure unchanged; only modify citation links.
2. Ensure every in-text citation uses markdown format: ([citation text](url)).
3. Use ONLY URLs from the allowed list below. Replace any citation URL not in the list with the most relevant URL from the list, or remove the citation if no match.
4. Do not add new claims or content; only fix or adjust existing citations.
5. Preserve the report's language and {report_format} style.

Allowed URLs (use only these):
{allowed_list}

Report to improve:
---
{report}
---

Return the improved report in full, with no extra commentary."""

    try:
        improved = await create_chat_completion(
            model=config.smart_llm_model,
            messages=[
                {"role": "system", "content": "You are a precise citation editor. Output only the improved report text."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            llm_provider=config.smart_llm_provider,
            stream=False,
            websocket=None,
            max_tokens=config.smart_token_limit,
            llm_kwargs=config.llm_kwargs,
            cost_callback=cost_callback,
            **kwargs
        )
        return improved.strip() if improved else report
    except Exception as e:
        logger.warning(f"Citation improver failed, returning original report: {e}")
        return report


async def generate_report(
    query: str,
    context,
    agent_role_prompt: str,
    report_type: str,
    tone: Tone,
    report_source: str,
    websocket,
    cfg,
    main_topic: str = "",
    existing_headers: list = [],
    relevant_written_contents: list = [],
    cost_callback: callable = None,
    custom_prompt: str = "", # This can be any prompt the user chooses with the context
    headers=None,
    prompt_family: type[PromptFamily] | PromptFamily = PromptFamily,
    **kwargs
):
    """
    generates the final report
    Args:
        query:
        context:
        agent_role_prompt:
        report_type:
        websocket:
        tone:
        cfg:
        main_topic:
        existing_headers:
        relevant_written_contents:
        cost_callback:
        prompt_family: Family of prompts

    Returns:
        report:

    """
    allowed_urls = kwargs.pop("allowed_urls", None) or []
    context_str = format_context_for_report(context)
    if not allowed_urls and isinstance(context, list):
        allowed_urls = _extract_allowed_urls_from_context(context)

    generate_prompt = get_prompt_by_report_type(report_type, prompt_family)
    report = ""

    if report_type == "subtopic_report":
        content = f"{generate_prompt(query, existing_headers, relevant_written_contents, main_topic, context_str, report_format=cfg.report_format, tone=tone, total_words=cfg.total_words, language=cfg.language)}"
    elif custom_prompt:
        content = f"{custom_prompt}\n\nContext: {context_str}"
    else:
        content = f"{generate_prompt(query, context_str, report_source, report_format=cfg.report_format, tone=tone, total_words=cfg.total_words, language=cfg.language)}"

    if allowed_urls:
        allowed_preview = ", ".join(allowed_urls[:15])
        if len(allowed_urls) > 15:
            allowed_preview += f" (and {len(allowed_urls) - 15} more)"
        content += f"\n\nOnly use the following URLs for in-text citations (use no other URLs): {allowed_preview}"

    try:
        report = await create_chat_completion(
            model=cfg.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{agent_role_prompt}"},
                {"role": "user", "content": content},
            ],
            temperature=0.35,
            llm_provider=cfg.smart_llm_provider,
            stream=True,
            websocket=websocket,
            max_tokens=cfg.smart_token_limit,
            llm_kwargs=cfg.llm_kwargs,
            cost_callback=cost_callback,
            **kwargs
        )
    except Exception:
        try:
            report = await create_chat_completion(
                model=cfg.smart_llm_model,
                messages=[
                    {"role": "user", "content": f"{agent_role_prompt}\n\n{content}"},
                ],
                temperature=0.35,
                llm_provider=cfg.smart_llm_provider,
                stream=True,
                websocket=websocket,
                max_tokens=cfg.smart_token_limit,
                llm_kwargs=cfg.llm_kwargs,
                cost_callback=cost_callback,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Error in generate_report: {e}")

    return report
