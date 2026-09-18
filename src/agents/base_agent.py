"""Base Agent definition for Translational Biomedical Intelligence Platform.

Zero emoji characters in all outputs.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any
import pandas as pd
from src.tools.db_tool import ReadOnlyDatabaseTool


class BaseAgent(ABC):
    """Abstract base class for domain-specialized biomedical agents."""

    def __init__(self, name: str, role: str, description: str, db_tool: ReadOnlyDatabaseTool | None = None):
        self.name = name
        self.role = role
        self.description = description
        self.db_tool = db_tool or ReadOnlyDatabaseTool()
        self.execution_log: list[dict[str, Any]] = []

    def log_step(self, action: str, details: Any, elapsed_ms: float = 0.0) -> None:
        """Record an execution step."""
        self.execution_log.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "agent": self.name,
            "action": action,
            "details": details,
            "elapsed_ms": elapsed_ms,
        })

    @abstractmethod
    def run(self, query: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute agent analysis for the given query and optional prior context."""
        pass
