"""
IDE context detection and file path extraction strategies.
"""

import logging
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

log = logging.getLogger(__name__)


class IDEType(Enum):
    """Supported IDE types."""

    CLAUDE = "claude"
    UNKNOWN = "unknown"


class IDEContextStrategy(ABC):
    """Abstract base class for IDE context strategies."""

    @abstractmethod
    def detect(self) -> bool:
        """Detect if this IDE context is active."""
        pass

    @abstractmethod
    def get_file_paths(self) -> Optional[List[str]]:
        """Extract file paths from the IDE context."""
        pass

    @abstractmethod
    def get_ide_type(self) -> IDEType:
        """Return the IDE type."""
        pass


class ClaudeContextStrategy(IDEContextStrategy):
    """Strategy for Claude Code IDE context."""

    def detect(self) -> bool:
        """Detect Claude Code context by checking for CLAUDE_* environment variables."""
        # Claude sets various environment variables during hook execution
        claude_vars = [
            "CLAUDE_FILE_PATHS",
            "CLAUDE_TOOL_NAME",
            "CLAUDE_PROJECT_DIR",
        ]
        return any(os.environ.get(var) for var in claude_vars)

    def get_file_paths(self) -> Optional[List[str]]:
        """
        Extract file paths from Claude environment variables.

        Claude provides:
        - CLAUDE_FILE_PATHS: Space-separated list of file paths (for multi-file operations)
        """
        file_paths = []

        # Check for multiple file paths first
        claude_file_paths = os.environ.get("CLAUDE_FILE_PATHS")
        if claude_file_paths:
            # Split space-separated paths and filter empty strings
            paths = [p.strip() for p in claude_file_paths.split() if p.strip()]
            file_paths.extend(paths)
            log.debug(f"Found {len(paths)} files in CLAUDE_FILE_PATHS")

        return file_paths if file_paths else None

    def get_ide_type(self) -> IDEType:
        """Return Claude IDE type."""
        return IDEType.CLAUDE


class IDEContextDetector:
    """
    Detects IDE context and extracts file paths using appropriate strategy.
    """

    def __init__(self) -> None:
        """Initialize with all available strategies."""
        self.strategies: List[IDEContextStrategy] = [
            ClaudeContextStrategy(),
        ]
        self._detected_strategy: Optional[IDEContextStrategy] = None

    def detect_context(self) -> IDEType:
        """
        Detect the current IDE context.

        Returns:
            IDEType: The detected IDE type, or UNKNOWN if none detected
        """
        for strategy in self.strategies:
            if strategy.detect():
                self._detected_strategy = strategy
                ide_type = strategy.get_ide_type()
                log.info(f"Detected {ide_type.value} IDE context")
                return ide_type

        log.debug("No specific IDE context detected")
        return IDEType.UNKNOWN

    def get_file_paths(self) -> Optional[List[str]]:
        """
        Get file paths from the detected IDE context.

        Returns:
            List of file paths if available, None otherwise
        """
        if self._detected_strategy:
            paths = self._detected_strategy.get_file_paths()
            if paths:
                log.info(
                    f"Extracted {len(paths)} file path(s) from {self._detected_strategy.get_ide_type().value} context"
                )
            return paths

        # Try each strategy if no context was previously detected
        for strategy in self.strategies:
            if strategy.detect():
                paths = strategy.get_file_paths()
                if paths:
                    log.info(
                        f"Extracted {len(paths)} file path(s) from {strategy.get_ide_type().value} context"
                    )
                    return paths

        return None

    def get_detected_ide(self) -> IDEType:
        """
        Get the detected IDE type.

        Returns:
            IDEType: The detected IDE type, or UNKNOWN if none detected
        """
        if self._detected_strategy:
            return self._detected_strategy.get_ide_type()

        # Re-detect if needed
        return self.detect_context()


def get_files_from_environment() -> Optional[List[str]]:
    """
    Convenience function to get file paths from the current IDE context.

    Returns:
        List of file paths if available, None otherwise
    """
    detector = IDEContextDetector()
    detector.detect_context()
    return detector.get_file_paths()
