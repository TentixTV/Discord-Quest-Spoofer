"""
Discord Local IPC / Rich Presence Client
Communicates directly with the running Discord Desktop client via Windows named pipe.
"""

import os
import time
import struct
import json
import threading
from typing import Optional

OP_HANDSHAKE = 0
OP_FRAME = 1
OP_CLOSE = 2
OP_PING = 3
OP_PONG = 4

class DiscordIPCClient:
    def __init__(self, client_id: str):
        self.client_id = str(client_id)
        self.pipe_file = None
        self.connected = False
        self._lock = threading.Lock()

    def _find_pipe(self):
        for i in range(10):
            pipe_path = rf"\\.\pipe\discord-ipc-{i}"
            if os.path.exists(pipe_path):
                return pipe_path
        return None

    def connect(self) -> bool:
        """Connects to Discord's local IPC pipe and performs handshake."""
        for i in range(10):
            pipe_path = rf"\\.\pipe\discord-ipc-{i}"
            try:
                self.pipe_file = open(pipe_path, "r+b", buffering=0)
                # Send Handshake
                self._send(OP_HANDSHAKE, {"v": 1, "client_id": self.client_id})
                op, resp = self._read()
                if op == OP_FRAME and resp and resp.get("evt") == "READY":
                    self.connected = True
                    return True
                else:
                    self.close()
            except Exception:
                if self.pipe_file:
                    try:
                        self.pipe_file.close()
                    except Exception:
                        pass
                    self.pipe_file = None
                continue
        return False

    def _send(self, opcode: int, payload: dict):
        if not self.pipe_file:
            return
        data = json.dumps(payload).encode("utf-8")
        header = struct.pack("<II", opcode, len(data))
        self.pipe_file.write(header + data)
        self.pipe_file.flush()

    def _read(self):
        if not self.pipe_file:
            return None, None
        try:
            header = self.pipe_file.read(8)
            if len(header) < 8:
                return None, None
            opcode, length = struct.unpack("<II", header)
            data = self.pipe_file.read(length)
            return opcode, json.loads(data.decode("utf-8", errors="ignore"))
        except Exception:
            return None, None

    def set_activity(self, details: Optional[str] = None, state: Optional[str] = None, start_time: Optional[int] = None, pid: Optional[int] = None):
        """Sets Rich Presence activity in Discord safely."""
        if not self.connected or not self.pipe_file:
            return False
        with self._lock:
            try:
                act_inner = {
                    "timestamps": {
                        "start": start_time or int(time.time())
                    },
                    "instance": True
                }
                if details and isinstance(details, str) and details.strip():
                    act_inner["details"] = details.strip()
                if state and isinstance(state, str) and state.strip():
                    act_inner["state"] = state.strip()

                activity_payload = {
                    "cmd": "SET_ACTIVITY",
                    "args": {
                        "pid": pid or os.getpid(),
                        "activity": act_inner
                    },
                    "nonce": f"rpc-{int(time.time()*1000)}"
                }
                self._send(OP_FRAME, activity_payload)
                self._read()
                return True
            except Exception:
                self.connected = False
                return False

    def clear_activity(self):
        """Clears Rich Presence activity."""
        if not self.connected or not self.pipe_file:
            return
        with self._lock:
            try:
                payload = {
                    "cmd": "SET_ACTIVITY",
                    "args": {
                        "pid": os.getpid(),
                        "activity": None
                    },
                    "nonce": f"rpc-clear-{int(time.time())}"
                }
                self._send(OP_FRAME, payload)
                self._read()
            except Exception:
                pass

    def close(self):
        """Closes IPC named pipe connection."""
        self.connected = False
        if self.pipe_file:
            try:
                self.clear_activity()
                self._send(OP_CLOSE, {})
                self.pipe_file.close()
            except Exception:
                pass
            self.pipe_file = None
