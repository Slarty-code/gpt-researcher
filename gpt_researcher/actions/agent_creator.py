"""Agent creation and selection utilities for GPT Researcher.

This module provides functions to automatically select and configure
the appropriate research agent based on the query type.
"""

import json
import logging
import re

import json_repair

from ..prompts import PromptFamily
from ..utils.llm import create_chat_completion

logger = logging.getLogger(__name__)

# #region debug instrumentation
def _debug_log(location, message, data, hypothesis_id=None):
    try:
        log_path = r"c:\dev\gpt-researcher\.cursor\debug.log"
        log_entry = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(__import__("time").time() * 1000)
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass
# #endregion

async def choose_agent(
    query,
    cfg,
    parent_query=None,
    cost_callback: callable = None,
    headers=None,
    prompt_family: type[PromptFamily] | PromptFamily = PromptFamily,
    **kwargs
):
    """
    Chooses the agent automatically
    Args:
        parent_query: In some cases the research is conducted on a subtopic from the main query.
            The parent query allows the agent to know the main context for better reasoning.
        query: original query
        cfg: Config
        cost_callback: callback for calculating llm costs
        prompt_family: Family of prompts

    Returns:
        agent: Agent name
        agent_role_prompt: Agent role prompt
    """
    query = f"{parent_query} - {query}" if parent_query else f"{query}"
    response = None  # Initialize response to ensure it's defined
    # #region debug instrumentation
    _debug_log("agent_creator.py:34", "choose_agent entry", {"query": query, "response_init": str(response)}, "A")
    # #endregion

    try:
        # #region debug instrumentation
        _debug_log("agent_creator.py:37", "before create_chat_completion", {"response_before": str(response)}, "A")
        # #endregion
        response = await create_chat_completion(
            model=cfg.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{prompt_family.auto_agent_instructions()}"},
                {"role": "user", "content": f"task: {query}"},
            ],
            temperature=0.15,
            llm_provider=cfg.smart_llm_provider,
            llm_kwargs=cfg.llm_kwargs,
            cost_callback=cost_callback,
            **kwargs
        )
        # #region debug instrumentation
        _debug_log("agent_creator.py:49", "after create_chat_completion", {"response_after": str(response), "response_type": type(response).__name__, "response_is_none": response is None}, "A")
        # #endregion

        agent_dict = json.loads(response)
        return agent_dict["server"], agent_dict["agent_role_prompt"]

    except Exception as e:
        # #region debug instrumentation
        _debug_log("agent_creator.py:53", "exception caught in choose_agent", {"exception_type": type(e).__name__, "exception_msg": str(e), "response_in_except": str(response), "response_is_none": response is None}, "A")
        # #endregion
        return await handle_json_error(response)


async def handle_json_error(response: str | None):
    """Handle JSON parsing errors from LLM responses.

    Attempts to recover agent information from malformed JSON responses
    using json_repair and regex extraction as fallbacks.

    Args:
        response: The LLM response string that failed initial JSON parsing.

    Returns:
        A tuple of (agent_name, agent_role_prompt). Returns default agent
        if all parsing attempts fail.
    """
    # #region debug instrumentation
    _debug_log("agent_creator.py:57", "handle_json_error entry", {"response": str(response), "response_type": type(response).__name__, "response_is_none": response is None}, "C")
    # #endregion
    try:
        agent_dict = json_repair.loads(response)
        if agent_dict.get("server") and agent_dict.get("agent_role_prompt"):
            return agent_dict["server"], agent_dict["agent_role_prompt"]
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        # #region debug instrumentation
        _debug_log("agent_creator.py:62", "json_repair exception", {"error_type": error_type, "error_msg": error_msg, "response": str(response), "response_is_none": response is None}, "C")
        # #endregion
        logger.warning(
            f"Failed to parse agent JSON with json_repair: {error_type}: {error_msg}",
            exc_info=True
        )
        if response:
            logger.debug(f"LLM response that failed to parse: {response[:500]}...")

    # #region debug instrumentation
    _debug_log("agent_creator.py:72", "before extract_json_with_regex", {"response": str(response), "response_type": type(response).__name__, "response_is_none": response is None}, "C")
    # #endregion
    json_string = extract_json_with_regex(response)
    if json_string:
        try:
            json_data = json.loads(json_string)
            return json_data["server"], json_data["agent_role_prompt"]
        except json.JSONDecodeError as e:
            logger.warning(
                f"Failed to decode JSON from regex extraction: {str(e)}",
                exc_info=True
            )

    logger.info("No valid JSON found in LLM response. Falling back to default agent.")
    return "Default Agent", (
        "You are an AI critical thinker research assistant. Your sole purpose is to write well written, "
        "critically acclaimed, objective and structured reports on given text."
    )


def extract_json_with_regex(response: str | None) -> str | None:
    """Extract JSON object from a string using regex.

    Attempts to find the first JSON object pattern in the response string.

    Args:
        response: The string to search for JSON content.

    Returns:
        The extracted JSON string if found, None otherwise.
    """
    # #region debug instrumentation
    _debug_log("agent_creator.py:90", "extract_json_with_regex entry", {"response": str(response), "response_type": type(response).__name__, "response_is_none": response is None}, "D")
    # #endregion
    if not response:
        return None
    json_match = re.search(r"{.*?}", response, re.DOTALL)
    if json_match:
        return json_match.group(0)
    return None
