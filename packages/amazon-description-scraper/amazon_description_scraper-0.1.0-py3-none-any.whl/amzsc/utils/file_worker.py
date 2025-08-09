import json
import threading
from pathlib import Path
from typing import Dict

lock = threading.Lock()


def write_to_json(path: Path, row: Dict[str, str]) -> None:
    with lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
