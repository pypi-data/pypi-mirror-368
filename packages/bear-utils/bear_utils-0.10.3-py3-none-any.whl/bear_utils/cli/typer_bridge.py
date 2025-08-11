"""A simple bridge for augmenting Typer with alias support and command execution for interactive use."""

from collections.abc import Callable
import shlex
from typing import Any, TypedDict

from rich.console import Console
from singleton_base import SingletonBase
from typer import Exit, Typer
from typer.models import CommandInfo

from bear_utils.logger_manager import AsyncLoggerProtocol, LoggerProtocol


class CommandMeta(TypedDict):
    """Metadata for a Typer command."""

    name: str
    help: str
    hidden: bool


def get_command_meta(command: CommandInfo) -> CommandMeta:
    """Extract metadata from a Typer command."""
    return {
        "name": command.name or (command.callback.__name__ if command.callback else "unknown"),
        "help": (command.callback.__doc__ if command.callback else None) or "No description available",
        "hidden": command.hidden,
    }


# TODO: Add support for usage statements for a more robust help system


class TyperBridge(SingletonBase):
    """Simple bridge for Typer command execution."""

    def __init__(self, typer_app: Typer, console: AsyncLoggerProtocol | LoggerProtocol | Console) -> None:
        """Initialize the TyperBridge with a Typer app instance."""
        self.app: Typer = typer_app
        self.console: AsyncLoggerProtocol | LoggerProtocol | Console = console or Console()
        self.command_meta: dict[str, CommandMeta] = {}
        self.ignore_list: list[str] = []

    def alias(self, *alias_names: str) -> Callable[..., Callable[..., Any]]:
        """Register aliases as hidden Typer commands."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            for alias in alias_names:
                self.app.command(name=alias, hidden=True)(func)
            return func

        return decorator

    def ignore(self) -> Callable[..., Callable[..., Any]]:
        """Decorator to set an internal attribute so other code can ignore this command."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            func._ignore = True  # type: ignore[attr-defined]
            self.ignore_list.append(func.__name__)
            return func

        return decorator

    def execute_command(self, command_string: str) -> bool:
        """Execute command via Typer. Return True if successful."""
        try:
            parts: list[str] = shlex.split(command_string.strip())
            if not parts:
                return False
            self.app(parts, standalone_mode=False)
            return True
        except Exit:
            return True
        except Exception as e:
            if isinstance(self.console, Console):
                self.console.print(f"[red]Error executing command: {e}[/red]")
            else:
                self.console.error(f"Error executing command: {e}", exc_info=True)
            return False

    def bootstrap_command_meta(self) -> None:
        """Bootstrap command metadata from the Typer app."""
        if not self.command_meta:
            for cmd in self.app.registered_commands:
                cmd_meta: CommandMeta = get_command_meta(command=cmd)
                self.command_meta[cmd_meta["name"]] = cmd_meta

    def get_all_command_info(self, show_hidden: bool = False) -> dict[str, CommandMeta]:
        """Get all command information from the Typer app."""
        if not self.command_meta:
            self.bootstrap_command_meta()
        if not show_hidden:
            return {name: meta for name, meta in self.command_meta.items() if not meta["hidden"]}
        return self.command_meta

    def get_command_info(self, command_name: str) -> CommandMeta | None:
        """Get metadata for a specific command."""
        if not self.command_meta:
            self.bootstrap_command_meta()
        return self.command_meta.get(command_name)
