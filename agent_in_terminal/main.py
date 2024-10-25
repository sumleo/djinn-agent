import asyncio
import os

from anthropic.types.beta import BetaTextBlockParam
from rich.prompt import Prompt
from rich.text import Text

from agent_in_terminal.constant.message import Sender
from agent_in_terminal.loop import APIProvider, console_loop
from agent_in_terminal.utils.console import ConsolePrinter

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

LLM_MODEL = "claude-3-5-sonnet-20241022"


async def main():

    # Initialize the console printer
    console_printer = ConsolePrinter()

    # Print the logo
    console_printer.print_logo()

    # Create a message list
    message_list = []

    # Start the console loop
    while True:
        # Get the user input
        user_input = Prompt.ask(Text("You", style="bold blue"))

        # Check if the user wants to exit
        if user_input.lower() == "exit":
            console_printer.print_goodbye()
            break

        # Create a user message
        user_message = {
            "role": Sender.USER,
            "content": [BetaTextBlockParam(type="text", text=user_input)],
        }

        # Append the user message to the message list
        message_list.append(user_message)

        # Run the console loop
        message_list = await console_loop(
            model=LLM_MODEL,
            messages=message_list,
            provider=APIProvider.ANTHROPIC,
            system_prompt_suffix="",
            output_callback=console_printer.print_agent_message,
            tool_output_callback=console_printer.print_tool_result_message,
            api_response_callback=lambda x, y, z: print(x, y, z),
            api_key=ANTHROPIC_API_KEY,
        )


if __name__ == "__main__":
    asyncio.new_event_loop().run_until_complete(main())
