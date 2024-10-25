"""
Agentic sampling loop that calls the Anthropic API and local implementation of anthropic-defined computer use tools.
"""

import asyncio
import os
import platform
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

import httpx
from anthropic import (Anthropic, AnthropicBedrock, AnthropicVertex, APIError,
                       APIResponseValidationError, APIStatusError)
from anthropic.types.beta import (BetaCacheControlEphemeralParam,
                                  BetaContentBlockParam, BetaImageBlockParam,
                                  BetaMessage, BetaMessageParam, BetaTextBlock,
                                  BetaTextBlockParam, BetaToolResultBlockParam,
                                  BetaToolUseBlockParam)

from agent_in_terminal.constant.message import Sender
from agent_in_terminal.tools import (BashTool, EditTool, ToolCollection,
                                     ToolResult)

COMPUTER_USE_BETA_FLAG = "computer-use-2024-10-22"
PROMPT_CACHING_BETA_FLAG = "prompt-caching-2024-07-31"
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


PROVIDER_TO_DEFAULT_MODEL_NAME: dict[APIProvider, str] = {
    APIProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
    APIProvider.BEDROCK: "anthropic.claude-3-5-sonnet-20241022-v2:0",
    APIProvider.VERTEX: "claude-3-5-sonnet-v2@20241022",
}

# We encourage modifying this system prompt to ensure the model has context for the
# environment it is running in, and to provide any additional information that may be
# helpful for the task at hand.
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilising a machine with {platform.system()} system using {platform.machine()} architecture with internet access.
* Your current working directory is {os.path.abspath(".")}.
* There is no GUI available, only a bash tool and a text editor tool.
* Your task is to interact with the computer using the bash tool and text editor tool to help the user.
* You can feel free to install {platform.system()} applications with your bash tool. Use curl instead of wget.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_editor or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>
"""


async def console_loop(
    *,
    model: str,
    provider: APIProvider,
    system_prompt_suffix: str,
    messages: list[BetaMessageParam],
    output_callback: Callable[[BetaContentBlockParam], None],
    tool_output_callback: Callable[[ToolResult, str], None],
    api_response_callback: Callable[
        [httpx.Request, httpx.Response | object | None, Exception | None], None
    ],
    api_key: str,
    max_tokens: int = 4096,
):
    """
    Agentic sampling loop for the assistant/tool interaction of computer use.
    """
    tool_collection = ToolCollection(
        BashTool(),
        EditTool(),
    )

    system = BetaTextBlockParam(
        type="text",
        text=f"{SYSTEM_PROMPT}{' ' + system_prompt_suffix if system_prompt_suffix else ''}",
    )

    while True:
        enable_prompt_caching = False
        betas = [COMPUTER_USE_BETA_FLAG]
        if provider == APIProvider.ANTHROPIC:
            client = Anthropic(api_key=api_key)
            enable_prompt_caching = True
        elif provider == APIProvider.VERTEX:
            client = AnthropicVertex()
        elif provider == APIProvider.BEDROCK:
            client = AnthropicBedrock()

        if enable_prompt_caching:
            betas.append(PROMPT_CACHING_BETA_FLAG)
            _inject_prompt_caching(messages)
            # Is it ever worth it to bust the cache with prompt caching?
            system["cache_control"] = {"type": "ephemeral"}

        # Call the API
        # we use raw_response to provide debug information to streamlit. Your
        # implementation may be able to call the SDK directly with:
        # `response = client.messages.create(...)` instead.
        try:
            raw_response = client.beta.messages.with_raw_response.create(
                max_tokens=max_tokens,
                messages=messages,
                model=model,
                system=[system],
                tools=tool_collection.to_params(),
                betas=betas,
            )
        except (APIStatusError, APIResponseValidationError) as e:
            # api_response_callback(e.request, e.response, e)
            return messages
        except APIError as e:
            # api_response_callback(e.request, e.body, e)
            return messages

        # api_response_callback(
        #     raw_response.http_response.request, raw_response.http_response, None
        # )

        response = raw_response.parse()

        response_params = _response_to_params(response)
        messages.append(
            {
                "role": "assistant",
                "content": response_params,
            }
        )

        tool_result_content: list[BetaToolResultBlockParam] = []
        for content_block in response_params:
            output_callback(content_block)
            if content_block["type"] == "tool_use":
                result = await tool_collection.run(
                    name=content_block["name"],
                    tool_input=cast(dict[str, Any], content_block["input"]),
                )
                tool_result_content.append(
                    _make_api_tool_result(result, content_block["id"])
                )
                tool_output_callback(result)

        if not tool_result_content:
            return messages

        messages.append({"content": tool_result_content, "role": "user"})


def _response_to_params(
    response: BetaMessage,
) -> list[BetaTextBlockParam | BetaToolUseBlockParam]:
    res: list[BetaTextBlockParam | BetaToolUseBlockParam] = []
    for block in response.content:
        if isinstance(block, BetaTextBlock):
            res.append({"type": "text", "text": block.text})
        else:
            res.append(cast(BetaToolUseBlockParam, block.model_dump()))
    return res


def _inject_prompt_caching(
    messages: list[BetaMessageParam],
):
    """
    Set cache breakpoints for the 3 most recent turns
    one cache breakpoint is left for tools/system prompt, to be shared across sessions
    """

    breakpoints_remaining = 3
    for message in reversed(messages):
        if message["role"] == "user" and isinstance(
            content := message["content"], list
        ):
            if breakpoints_remaining:
                breakpoints_remaining -= 1
                content[-1]["cache_control"] = BetaCacheControlEphemeralParam(
                    {"type": "ephemeral"}
                )
            else:
                content[-1].pop("cache_control", None)
                # we'll only every have one extra turn per loop
                break


def _make_api_tool_result(
    result: ToolResult, tool_use_id: str
) -> BetaToolResultBlockParam:
    """Convert an agent ToolResult to an API ToolResultBlockParam."""
    tool_result_content: list[BetaTextBlockParam | BetaImageBlockParam] | str = []
    is_error = False
    if result.error:
        is_error = True
        tool_result_content = _maybe_prepend_system_tool_result(result, result.error)
    else:
        if result.output:
            tool_result_content.append(
                {
                    "type": "text",
                    "text": _maybe_prepend_system_tool_result(result, result.output),
                }
            )
        if result.base64_image:
            tool_result_content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": result.base64_image,
                    },
                }
            )
    return {
        "type": "tool_result",
        "content": tool_result_content,
        "tool_use_id": tool_use_id,
        "is_error": is_error,
    }


def _maybe_prepend_system_tool_result(result: ToolResult, result_text: str):
    if result.system:
        result_text = f"<system>{result.system}</system>\n{result_text}"
    return result_text


if __name__ == "__main__":
    print(CLAUDE_API_KEY)

    asyncio.new_event_loop().run_until_complete(
        console_loop(
            model="claude-3-5-sonnet-20241022",
            provider=APIProvider.ANTHROPIC,
            system_prompt_suffix="",
            messages=[
                {
                    "role": Sender.USER,
                    "content": [
                        BetaTextBlockParam(
                            type="text", text="list current folder files"
                        )
                    ],
                }
            ],
            output_callback=lambda x: print(x),
            tool_output_callback=lambda x, y: print(x, y),
            api_response_callback=lambda x, y, z: print(x, y, z),
            api_key=CLAUDE_API_KEY,
        )
    )
