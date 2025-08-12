import atexit
import contextlib
import signal
import sys
import threading
from typing import Any

from .terminal_instance import TerminalInstance


class TerminalManager:
    def __init__(self) -> None:
        self.terminals: dict[str, TerminalInstance] = {}
        self._lock = threading.Lock()
        self.default_terminal_id = "default"

        self._register_cleanup_handlers()

    def create_terminal(
        self, terminal_id: str | None = None, inputs: list[str] | None = None
    ) -> dict[str, Any]:
        if terminal_id is None:
            terminal_id = self.default_terminal_id

        with self._lock:
            if terminal_id in self.terminals:
                raise ValueError(f"Terminal '{terminal_id}' already exists")

            initial_command = None
            if inputs:
                command_parts: list[str] = []
                for input_item in inputs:
                    if input_item == "Enter":
                        initial_command = " ".join(command_parts) + "\n"
                        break
                    if input_item.startswith("literal:"):
                        command_parts.append(input_item[8:])
                    elif input_item not in [
                        "Space",
                        "Tab",
                        "Backspace",
                    ]:
                        command_parts.append(input_item)

            try:
                terminal = TerminalInstance(terminal_id, initial_command)
                self.terminals[terminal_id] = terminal

                if inputs and not initial_command:
                    terminal.send_input(inputs)
                    result = terminal.wait(2.0)
                else:
                    result = terminal.wait(1.0)

                result["message"] = f"Terminal '{terminal_id}' created successfully"

            except (OSError, ValueError, RuntimeError) as e:
                raise RuntimeError(f"Failed to create terminal '{terminal_id}': {e}") from e
            else:
                return result

    def send_input(
        self, terminal_id: str | None = None, inputs: list[str] | None = None
    ) -> dict[str, Any]:
        if terminal_id is None:
            terminal_id = self.default_terminal_id

        if not inputs:
            raise ValueError("No inputs provided")

        with self._lock:
            if terminal_id not in self.terminals:
                raise ValueError(f"Terminal '{terminal_id}' not found")

            terminal = self.terminals[terminal_id]

        try:
            terminal.send_input(inputs)
            result = terminal.wait(2.0)
            result["message"] = f"Input sent to terminal '{terminal_id}'"
        except (OSError, ValueError, RuntimeError) as e:
            raise RuntimeError(f"Failed to send input to terminal '{terminal_id}': {e}") from e
        else:
            return result

    def wait_terminal(
        self, terminal_id: str | None = None, duration: float = 1.0
    ) -> dict[str, Any]:
        if terminal_id is None:
            terminal_id = self.default_terminal_id

        with self._lock:
            if terminal_id not in self.terminals:
                raise ValueError(f"Terminal '{terminal_id}' not found")

            terminal = self.terminals[terminal_id]

        try:
            result = terminal.wait(duration)
            result["message"] = f"Waited {duration}s on terminal '{terminal_id}'"
        except (OSError, ValueError, RuntimeError) as e:
            raise RuntimeError(f"Failed to wait on terminal '{terminal_id}': {e}") from e
        else:
            return result

    def close_terminal(self, terminal_id: str | None = None) -> dict[str, Any]:
        if terminal_id is None:
            terminal_id = self.default_terminal_id

        with self._lock:
            if terminal_id not in self.terminals:
                raise ValueError(f"Terminal '{terminal_id}' not found")

            terminal = self.terminals.pop(terminal_id)

        try:
            terminal.close()
        except (OSError, ValueError, RuntimeError) as e:
            raise RuntimeError(f"Failed to close terminal '{terminal_id}': {e}") from e
        else:
            return {
                "terminal_id": terminal_id,
                "message": f"Terminal '{terminal_id}' closed successfully",
                "snapshot": "",
                "is_running": False,
            }

    def get_terminal_snapshot(self, terminal_id: str | None = None) -> dict[str, Any]:
        if terminal_id is None:
            terminal_id = self.default_terminal_id

        with self._lock:
            if terminal_id not in self.terminals:
                raise ValueError(f"Terminal '{terminal_id}' not found")

            terminal = self.terminals[terminal_id]

        return terminal.get_snapshot()

    def list_terminals(self) -> dict[str, Any]:
        with self._lock:
            terminal_info = {}
            for tid, terminal in self.terminals.items():
                terminal_info[tid] = {
                    "is_running": terminal.is_running,
                    "is_alive": terminal.is_alive(),
                    "process_id": terminal.process.pid if terminal.process else None,
                }

        return {"terminals": terminal_info, "total_count": len(terminal_info)}

    def cleanup_dead_terminals(self) -> None:
        with self._lock:
            dead_terminals = []
            for tid, terminal in self.terminals.items():
                if not terminal.is_alive():
                    dead_terminals.append(tid)

            for tid in dead_terminals:
                terminal = self.terminals.pop(tid)
                with contextlib.suppress(Exception):
                    terminal.close()

    def close_all_terminals(self) -> None:
        with self._lock:
            terminals_to_close = list(self.terminals.values())
            self.terminals.clear()

        for terminal in terminals_to_close:
            with contextlib.suppress(Exception):
                terminal.close()

    def _register_cleanup_handlers(self) -> None:
        atexit.register(self.close_all_terminals)

        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, self._signal_handler)

    def _signal_handler(self, _signum: int, _frame: Any) -> None:
        self.close_all_terminals()
        sys.exit(0)


_terminal_manager = TerminalManager()


def get_terminal_manager() -> TerminalManager:
    return _terminal_manager
