from rich.console import Console
from rich.panel import Panel

import rich.progress

root_console = Console()
debug = False

PREFIX = "[grey58]> [/grey58]"
# TODO: tee to file here

def _get_console(console):
    if console:
        return console
    else:
        return root_console

## Display Utilities
def print_top_header(text,console=None):
    console = _get_console(console)
    console.rule(f"[bold cyan]{text}", align="center")

def print_header(text, console=None):
    console = _get_console(console)
    # console.rule(f"[bold bright_magenta]{text}", style="bright_magenta", align="center")
    console.print(Panel(f"{text}", style="bright_magenta"))


def print_complete(text, console=None):
    console = _get_console(console)
    # console.rule(
    #     f"[bold green]:white_check_mark: {text}",
    #     style="green",
    #     align="center",
    # )
    # console.print(Panel(f":white_check_mark: {text}", style="green"))
    console.print(f"{PREFIX}:white_check_mark:  {text}", style="green")

def print_notification(text,console=None):
    console = _get_console(console)
    console.print(
        Panel(
            f"[bold bright_cyan]{text}[/bold bright_cyan]",
            title="[bold bright_cyan]:information:  Notification",
            title_align="left",
            style="bright_cyan",
        )
    )

def print_warning(text, console=None):
    console = _get_console(console)
    console.print(
        Panel(
            f"[bold yellow]{text}[/bold yellow]",
            title="[bold yellow]:warning:  Warning",
            title_align="left",
            style="yellow",
        )
    )


def print_error(text, console=None):
    console = _get_console(console)
    console.print(
        Panel(
            f"[bold red]{text}[/bold red]",
            title="[bold red]:warning:  Error",
            title_align="left",
            style="red",
        )
    )


def print_log(text, console=None):
    console = _get_console(console)
    console.print(f"{PREFIX}{text}")

def print_debug(text,console = None):
    if not debug:
        return
    console = _get_console(console)
    console.print(
        Panel(
            f"[bold grey58]{text}[/bold grey58]",
            title="[bold grey58]Verbose log",
            title_align="left",
            style="grey58",
        )
    )

def open_file(*args, **kwargs):
    if "description" in kwargs:
        # add prefix and suffix padding
        kwargs["description"] = f'{PREFIX}{kwargs["description"]}'.ljust(30, " ")
    return rich.progress.open(
        *args, **kwargs
    )
