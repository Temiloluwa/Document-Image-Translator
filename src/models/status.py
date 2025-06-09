from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Status:
    state: str
    progress: int = 0
    message: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

    def asdict(self):
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}
