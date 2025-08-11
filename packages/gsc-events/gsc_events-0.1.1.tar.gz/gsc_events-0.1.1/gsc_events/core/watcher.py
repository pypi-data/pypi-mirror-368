from collections.abc import Iterable
from typing import Dict, Tuple, List
from pathlib import Path

def get_files(path: Path) -> Iterable[Path]:
    return filter(Path.is_file, path.glob("event_*.jsonl"))

def tail(files: Iterable[Path]) -> Dict[Path, int]:
    return {file: file.stat().st_size for file in files}

def read(file: Path, offset: int) -> Tuple[List[str], str]:
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(offset)
        lines = f.read().splitlines()
        return lines, f.tell()