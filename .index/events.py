#!/usr/bin/env python3
"""
Event System for The Collectivist
Structured event emission for real-time pipeline progress updates
"""

from dataclasses import dataclass, asdict
from typing import Optional, Callable, Any, Dict
from datetime import datetime
from enum import Enum


class EventLevel(Enum):
    """Event severity levels"""
    INFO = "info"
    WARN = "warn" 
    ERROR = "error"
    SUCCESS = "success"


class EventStage(Enum):
    """Pipeline stages"""
    ANALYZE = "analyze"
    SCAN = "scan"
    DESCRIBE = "describe"
    RENDER = "render"


@dataclass
class PipelineEvent:
    """
    Structured event for pipeline progress updates.
    Designed for WebSocket streaming and UI consumption.
    """
    stage: str              # Current pipeline stage
    current_item: Optional[str] = None  # Item being processed
    progress_current: int = 0           # Current item number (i)
    progress_total: int = 0             # Total items (n)
    percent: float = 0.0               # Percentage complete (0-100)
    message: str = ""                  # Human-readable message
    level: str = EventLevel.INFO.value # Event level
    timestamp: str = ""                # ISO timestamp
    metadata: Dict[str, Any] = None    # Additional context

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
        
        # Auto-calculate percentage if not provided
        if self.percent == 0.0 and self.progress_total > 0:
            self.percent = (self.progress_current / self.progress_total) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class EventEmitter:
    """
    Event emitter for pipeline stages.
    Provides structured progress updates for real-time UI.
    """

    def __init__(self, callback: Optional[Callable[[PipelineEvent], None]] = None):
        self.callback = callback
        self._stage = ""
        self._total_items = 0
        self._current_item = 0

    def set_stage(self, stage: EventStage, total_items: int = 0):
        """Set current pipeline stage and total item count"""
        self._stage = stage.value
        self._total_items = total_items
        self._current_item = 0
        
        self.emit(
            message=f"Starting {stage.value} stage",
            level=EventLevel.INFO
        )

    def set_progress(self, current: int, item_name: Optional[str] = None):
        """Update progress within current stage"""
        self._current_item = current
        
        message = f"Processing item {current}/{self._total_items}"
        if item_name:
            message += f": {item_name}"
            
        self.emit(
            current_item=item_name,
            progress_current=current,
            progress_total=self._total_items,
            message=message,
            level=EventLevel.INFO
        )

    def success(self, message: str, **kwargs):
        """Emit success event"""
        self.emit(message=message, level=EventLevel.SUCCESS, **kwargs)

    def info(self, message: str, **kwargs):
        """Emit info event"""
        self.emit(message=message, level=EventLevel.INFO, **kwargs)

    def warn(self, message: str, **kwargs):
        """Emit warning event"""
        self.emit(message=message, level=EventLevel.WARN, **kwargs)

    def error(self, message: str, **kwargs):
        """Emit error event"""
        self.emit(message=message, level=EventLevel.ERROR, **kwargs)

    def complete_stage(self, message: Optional[str] = None):
        """Mark current stage as complete"""
        if not message:
            message = f"Completed {self._stage} stage"
            
        self.emit(
            progress_current=self._total_items,
            progress_total=self._total_items,
            percent=100.0,
            message=message,
            level=EventLevel.SUCCESS
        )

    def emit(
        self,
        current_item: Optional[str] = None,
        progress_current: Optional[int] = None,
        progress_total: Optional[int] = None,
        percent: Optional[float] = None,
        message: str = "",
        level: EventLevel = EventLevel.INFO,
        **metadata
    ):
        """Emit a structured event"""
        if not self.callback:
            return

        # Use current state as defaults
        event = PipelineEvent(
            stage=self._stage,
            current_item=current_item,
            progress_current=progress_current or self._current_item,
            progress_total=progress_total or self._total_items,
            percent=percent or 0.0,
            message=message,
            level=level.value if isinstance(level, EventLevel) else level,
            metadata=metadata
        )

        self.callback(event)


class ConsoleEventHandler:
    """
    Console event handler for CLI usage.
    Maintains backward compatibility with existing print-based output.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self._last_stage = ""

    def handle_event(self, event: PipelineEvent):
        """Handle pipeline event with console output"""
        # Stage headers
        if event.stage != self._last_stage:
            print(f"\n{'='*60}")
            print(f"STAGE: {event.stage.upper()}")
            print(f"{'='*60}")
            self._last_stage = event.stage

        # Progress indicators
        if event.level == EventLevel.ERROR.value:
            print(f"  [X] {event.message}")
        elif event.level == EventLevel.WARN.value:
            print(f"  [!] {event.message}")
        elif event.level == EventLevel.SUCCESS.value:
            print(f"  [OK] {event.message}")
        elif self.verbose:
            # Show progress for info events
            if event.progress_total > 0:
                print(f"  [{event.progress_current}/{event.progress_total}] {event.message}")
            else:
                print(f"  {event.message}")


def create_console_emitter(verbose: bool = True) -> EventEmitter:
    """Create event emitter with console output handler"""
    handler = ConsoleEventHandler(verbose)
    return EventEmitter(callback=handler.handle_event)


def create_silent_emitter() -> EventEmitter:
    """Create event emitter with no output (for testing)"""
    return EventEmitter(callback=None)


# Example usage for testing
if __name__ == '__main__':
    # Test console emitter
    emitter = create_console_emitter()
    
    # Simulate analyzer stage
    emitter.set_stage(EventStage.ANALYZE)
    emitter.info("Inspecting directory structure")
    emitter.info("Querying LLM for collection type")
    emitter.success("Collection type detected: repositories")
    emitter.complete_stage()
    
    # Simulate scanner stage
    emitter.set_stage(EventStage.SCAN, total_items=5)
    for i in range(1, 6):
        emitter.set_progress(i, f"repo-{i}")
    emitter.complete_stage()
    
    print("\n[OK] Event system test complete")