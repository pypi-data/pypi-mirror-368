import json
import os
from enum import Enum
from dataclasses import dataclass, field
from typing import List

class Severity(str, Enum):
    OK = "✅ OK"
    LOW = "🟢 Low"
    MEDIUM = "🟡 Warning"
    HIGH = "🔴 Critical"
    CRITICAL = "🛑 Failure"
    UNKNOWN = "❓ Unknown"

@dataclass
class AuditResult:
    title: str
    status: Severity
    messages: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "title": self.title,
            "status": self.status,
            "messages": self.messages
        }

# ✅ Used by main.py to write each plugin's result for HTML rendering
def save_audit_result_json(name, result: AuditResult):
    os.makedirs(".snapcheck", exist_ok=True)
    path = os.path.join(".snapcheck", f"{name}.json")
    with open(path, "w") as f:
        json.dump(result.to_dict(), f, indent=2)
