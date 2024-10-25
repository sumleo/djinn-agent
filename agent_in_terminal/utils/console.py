from typing import List

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class ConsolePrinter:
    def __init__(self):
        self.console = Console()
        self.prompt_history_list: List = []

    def print_logo(self):
        self.console.print(
            Panel(
                """
[bold blue]
   _____                         __    .__         ___________                  .__              .__   
  /  _  \    ____   ____   _____/  |_  |__| ____   \__    ___/__________  _____ |__| ____ _____  |  |  
 /  /_\  \  / ___\_/ __ \ /    \   __\ |  |/    \    |    |_/ __ \_  __ \/     \|  |/    \\\\__  \ |  |  
/    |    \/ /_/  >  ___/|   |  \  |   |  |   |  \   |    |\  ___/|  | \/  Y Y  \  |   |  \/ __ \|  |__
\____|__  /\___  / \___  >___|  /__|   |__|___|  /   |____| \___  >__|  |__|_|  /__|___|  (____  /____/
        \//_____/      \/     \/               \/               \/            \/        \/     \/      

                """,
                box=box.HEAVY,
                style="bold green",
            )
        )

    def print_goodbye(self):
        self.console.print(Panel("Goodbye!", box=box.ROUNDED, style="bold red"))

    def print_user_message(self, message):
        self.console.print(
            Panel(
                Text(f"You: {message.content}", style="bold blue"),
                box=box.DOUBLE,
                style="yellow",
                border_style="blue",
                subtitle="[italic]User[/italic]",
                subtitle_align="right",
            )
        )

    def print_agent_message(self, message):
        # Plain text message
        if "text" in message:
            self.console.print(
                Panel(
                    Text(f"Agent: {message['text']}", style="bold magenta"),
                    box=box.ROUNDED,
                    style="bold cyan",
                    border_style="magenta",
                    subtitle="[italic]Agent[/italic]",
                    subtitle_align="right",
                )
            )

        elif "type" in message and message["type"] == "tool_use":

            # Check if the tool is bash
            if message["name"] == "bash":
                self.console.print(
                    Panel(
                        Text(
                            f"Agent is trying to execute command: {message['input']['command']}",
                            style="bold magenta",
                        ),
                        box=box.DOUBLE,
                        style="yellow",
                        border_style="red",
                        subtitle="[italic]Tool Use: Bash[/italic]",
                        subtitle_align="right",
                    )
                )
            # Check if the tool is str_replace_editor
            elif message["name"] == "str_replace_editor":
                self.console.print(
                    Panel(
                        Text(
                            f"Agent is trying to {message['input']['command']} in {message['input']['path']}",
                            style="bold magenta",
                        ),
                        box=box.DOUBLE,
                        style="yellow",
                        border_style="green",
                        subtitle="[italic]Tool Use: String Replace[/italic]",
                        subtitle_align="right",
                    )
                )

            else:
                raise ValueError(f"Unknown tool type: {message['name']}")

        else:
            raise ValueError(f"Unknown message type: {message}")

    def print_tool_result_message(self, message):
        if message.output is None:
            return

        self.console.print(
            Panel(
                Text(f"Tool Result: {message.output}", style="bold green"),
                box=box.ROUNDED,
                style="bold green",
                border_style="green",
                subtitle="[italic]Tool Result[/italic]",
                subtitle_align="right",
            )
        )
