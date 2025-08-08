from typing import Any, Literal

from strix.tools.registry import register_tool

from .terminal_manager import get_terminal_manager


TerminalAction = Literal["new_terminal", "send_input", "wait", "close"]


@register_tool
def terminal_action(
    action: TerminalAction,
    inputs: list[str] | None = None,
    time: float | None = None,
    terminal_id: str | None = None,
) -> dict[str, Any]:
    def _validate_inputs(action_name: str, inputs: list[str] | None) -> None:
        if not inputs:
            raise ValueError(f"inputs parameter is required for {action_name} action")

    def _validate_time(time_param: float | None) -> None:
        if time_param is None:
            raise ValueError("time parameter is required for wait action")

    def _validate_action(action_name: str) -> None:
        raise ValueError(f"Unknown action: {action_name}")

    manager = get_terminal_manager()

    try:
        match action:
            case "new_terminal":
                return manager.create_terminal(terminal_id, inputs)

            case "send_input":
                _validate_inputs(action, inputs)
                assert inputs is not None
                return manager.send_input(terminal_id, inputs)

            case "wait":
                _validate_time(time)
                assert time is not None
                return manager.wait_terminal(terminal_id, time)

            case "close":
                return manager.close_terminal(terminal_id)

            case _:
                _validate_action(action)  # type: ignore[unreachable]

    except (ValueError, RuntimeError) as e:
        return {"error": str(e), "terminal_id": terminal_id, "snapshot": "", "is_running": False}
