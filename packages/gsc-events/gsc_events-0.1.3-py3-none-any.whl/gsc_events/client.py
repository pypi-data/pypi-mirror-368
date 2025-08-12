from typing import Optional, DefaultDict, List, Dict, Callable
from collections import defaultdict
from pathlib import Path
import os, time

from .core import get_files, tail, read, parse_line, emit_all

class GSCClient:
    def __init__(
        self, 
        filepath: Optional[str] = os.path.join(os.environ["LOCALAPPDATA"], "Plutonium", "storage", "t6", "raw", "scriptdata")
    ) -> None:
        self.filepath = filepath
        self._events: DefaultDict[str, List] = defaultdict(list)
        self._positions: Dict[Path, int] = {}

    def clear_events(self) -> None:
        for log in os.listdir(self.filepath):
            if log.startswith("event_") and log.endswith(".jsonl"):
                path = os.path.join(self.filepath, log)
                os.remove(path)

    def on(self, event: str) -> Callable:
        def decorator(func) -> Callable:
            self._events[event].append(func)
            return func
        return decorator

    def run(self) -> None:
        self._positions = {file: tail(file) for file in get_files(Path(self.filepath))}
        try:
            while True:
                files = list(get_files(Path(self.filepath)))
                results = {
                    file: read(file, self._positions.get(file, 0)) for file in files
                }

                events = filter(None, (
                    parse_line(line) for lines, _ in results.values() for line in lines
                ))

                emit_all(self._events, events)
                self._positions = {
                    file: offset for file, (_, offset) in results.items()
                }
                time.sleep(1)

        except KeyboardInterrupt:
            exit()