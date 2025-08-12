from typing import Any, ClassVar

from textual.widgets import Static

from .base_renderer import BaseToolRenderer
from .registry import register_tool_renderer


@register_tool_renderer
class TerminalRenderer(BaseToolRenderer):
    tool_name: ClassVar[str] = "terminal_action"
    css_classes: ClassVar[list[str]] = ["tool-call", "terminal-tool"]

    @classmethod
    def render(cls, tool_data: dict[str, Any]) -> Static:
        args = tool_data.get("args", {})
        status = tool_data.get("status", "unknown")
        result = tool_data.get("result", {})

        action = args.get("action", "unknown")
        inputs = args.get("inputs", [])
        terminal_id = args.get("terminal_id", "default")

        content = cls._build_sleek_content(action, inputs, terminal_id, result)

        css_classes = cls.get_css_classes(status)
        return Static(content, classes=css_classes)

    @classmethod
    def _build_sleek_content(
        cls,
        action: str,
        inputs: list[str],
        terminal_id: str,  # noqa: ARG003
        result: dict[str, Any],  # noqa: ARG003
    ) -> str:
        terminal_icon = ">_"

        if action in {"create", "new_terminal"}:
            command = cls._format_command(inputs) if inputs else "bash"
            return f"{terminal_icon} [#22c55e]${command}[/]"

        if action == "send_input":
            command = cls._format_command(inputs)
            return f"{terminal_icon} [#22c55e]${command}[/]"

        if action == "wait":
            return f"{terminal_icon} [dim]waiting...[/]"

        if action == "close":
            return f"{terminal_icon} [dim]close[/]"

        if action == "get_snapshot":
            return f"{terminal_icon} [dim]snapshot[/]"

        return f"{terminal_icon} [dim]{action}[/]"

    @classmethod
    def _format_command(cls, inputs: list[str]) -> str:
        if not inputs:
            return ""

        command_parts = []

        for input_item in inputs:
            if input_item == "Enter":
                break
            if input_item.startswith("literal:"):
                command_parts.append(input_item[8:])
            elif input_item in [
                "Space",
                "Tab",
                "Backspace",
                "Up",
                "Down",
                "Left",
                "Right",
                "Home",
                "End",
                "PageUp",
                "PageDown",
                "Insert",
                "Delete",
                "Escape",
            ] or input_item.startswith(("^", "C-", "S-", "A-", "F")):
                if input_item == "Space":
                    command_parts.append(" ")
                elif input_item == "Tab":
                    command_parts.append("\t")
                continue
            else:
                command_parts.append(input_item)

        command = "".join(command_parts).strip()

        if len(command) > 200:
            command = command[:197] + "..."

        return cls.escape_markup(command) if command else "bash"
