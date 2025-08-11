from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any


def log_json(event: str, **fields: Any) -> None:
    record = {"ts": datetime.utcnow().isoformat() + "Z", "event": event, **fields}
    sys.stdout.write(json.dumps(record) + "\n")
    sys.stdout.flush()
