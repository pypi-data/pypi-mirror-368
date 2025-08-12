from typing import Optional, Tuple, List, Dict, Callable
from collections.abc import Iterable
import json

def parse_line(line: str) -> Optional[Tuple[str, List]]:
    try:
        data = json.loads(line)
        event = data.get("event")
        args  = data.get("args", [])
        if not event:
            return
        return event, args
    
    except json.JSONDecodeError:
        print("[gsc-events] json decode error")
        return
    
def emit_all(
    handlers: Dict[str, List[Callable]],
    events: Iterable[Tuple[str, List]]
) -> None:
    for event, args in events:
        for func in handlers.get(event, []):
            try:
                func(*args)
            except Exception as e:
                print(f"[gsc-events] Error in handler '{func.__name__}': {e}")