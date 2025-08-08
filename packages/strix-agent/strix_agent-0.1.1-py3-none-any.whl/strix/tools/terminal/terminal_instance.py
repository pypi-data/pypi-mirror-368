import contextlib
import os
import pty
import select
import signal
import subprocess
import threading
import time
from typing import Any

import pyte


MAX_TERMINAL_SNAPSHOT_LENGTH = 10_000


class TerminalInstance:
    def __init__(self, terminal_id: str, initial_command: str | None = None) -> None:
        self.terminal_id = terminal_id
        self.process: subprocess.Popen[bytes] | None = None
        self.master_fd: int | None = None
        self.is_running = False
        self._output_lock = threading.Lock()
        self._reader_thread: threading.Thread | None = None

        self.screen = pyte.HistoryScreen(80, 24, history=1000)
        self.stream = pyte.ByteStream()
        self.stream.attach(self.screen)

        self._start_terminal(initial_command)

    def _start_terminal(self, initial_command: str | None = None) -> None:
        try:
            self.master_fd, slave_fd = pty.openpty()

            shell = "/bin/bash"

            self.process = subprocess.Popen(  # noqa: S603
                [shell, "-i"],
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                cwd="/workspace",
                preexec_fn=os.setsid,  # noqa: PLW1509 - Required for PTY functionality
            )

            os.close(slave_fd)

            self.is_running = True

            self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self._reader_thread.start()

            time.sleep(0.5)

            if initial_command:
                self._write_to_terminal(initial_command)

        except (OSError, ValueError) as e:
            raise RuntimeError(f"Failed to start terminal: {e}") from e

    def _read_output(self) -> None:
        while self.is_running and self.master_fd:
            try:
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                if ready:
                    data = os.read(self.master_fd, 4096)
                    if data:
                        with self._output_lock, contextlib.suppress(TypeError):
                            self.stream.feed(data)
                    else:
                        break
            except (OSError, ValueError):
                break

    def _write_to_terminal(self, data: str) -> None:
        if self.master_fd and self.is_running:
            try:
                os.write(self.master_fd, data.encode("utf-8"))
            except (OSError, ValueError) as e:
                raise RuntimeError("Terminal is no longer available") from e

    def send_input(self, inputs: list[str]) -> None:
        if not self.is_running:
            raise RuntimeError("Terminal is not running")

        for i, input_item in enumerate(inputs):
            if input_item.startswith("literal:"):
                literal_text = input_item[8:]
                self._write_to_terminal(literal_text)
            else:
                key_sequence = self._get_key_sequence(input_item)
                if key_sequence:
                    self._write_to_terminal(key_sequence)
                else:
                    self._write_to_terminal(input_item)

            time.sleep(0.05)

            if (
                i < len(inputs) - 1
                and not input_item.startswith("literal:")
                and not self._is_special_key(input_item)
                and not inputs[i + 1].startswith("literal:")
                and not self._is_special_key(inputs[i + 1])
            ):
                self._write_to_terminal(" ")

    def get_snapshot(self) -> dict[str, Any]:
        with self._output_lock:
            history_lines = [
                "".join(char.data for char in line_dict.values())
                for line_dict in self.screen.history.top
            ]

            current_lines = self.screen.display

            all_lines = history_lines + current_lines
            rendered_output = "\n".join(all_lines)

            if len(rendered_output) > MAX_TERMINAL_SNAPSHOT_LENGTH:
                rendered_output = rendered_output[-MAX_TERMINAL_SNAPSHOT_LENGTH:]
                truncated = True
            else:
                truncated = False

        return {
            "terminal_id": self.terminal_id,
            "snapshot": rendered_output,
            "is_running": self.is_running,
            "process_id": self.process.pid if self.process else None,
            "truncated": truncated,
        }

    def wait(self, duration: float) -> dict[str, Any]:
        time.sleep(duration)
        return self.get_snapshot()

    def close(self) -> None:
        self.is_running = False

        if self.process:
            with contextlib.suppress(OSError, ProcessLookupError):
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    self.process.wait()

        if self.master_fd:
            with contextlib.suppress(OSError):
                os.close(self.master_fd)
            self.master_fd = None

        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=1)

    def _is_special_key(self, key: str) -> bool:
        special_keys = {
            "Enter",
            "Space",
            "Backspace",
            "Tab",
            "Escape",
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
        } | {f"F{i}" for i in range(1, 13)}

        if key in special_keys:
            return True

        return bool(key.startswith(("^", "C-", "S-", "A-")))

    def _get_key_sequence(self, key: str) -> str | None:
        key_map = {
            "Enter": "\r",
            "Space": " ",
            "Backspace": "\x08",
            "Tab": "\t",
            "Escape": "\x1b",
            "Up": "\x1b[A",
            "Down": "\x1b[B",
            "Right": "\x1b[C",
            "Left": "\x1b[D",
            "Home": "\x1b[H",
            "End": "\x1b[F",
            "PageUp": "\x1b[5~",
            "PageDown": "\x1b[6~",
            "Insert": "\x1b[2~",
            "Delete": "\x1b[3~",
            "F1": "\x1b[11~",
            "F2": "\x1b[12~",
            "F3": "\x1b[13~",
            "F4": "\x1b[14~",
            "F5": "\x1b[15~",
            "F6": "\x1b[17~",
            "F7": "\x1b[18~",
            "F8": "\x1b[19~",
            "F9": "\x1b[20~",
            "F10": "\x1b[21~",
            "F11": "\x1b[23~",
            "F12": "\x1b[24~",
        }

        if key in key_map:
            return key_map[key]

        if key.startswith("^") and len(key) == 2:
            char = key[1].lower()
            return chr(ord(char) - ord("a") + 1) if "a" <= char <= "z" else None

        if key.startswith("C-") and len(key) == 3:
            char = key[2].lower()
            return chr(ord(char) - ord("a") + 1) if "a" <= char <= "z" else None

        return None

    def is_alive(self) -> bool:
        if not self.process:
            return False
        return self.process.poll() is None
