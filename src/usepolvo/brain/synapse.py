# brain/synapse.py
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from pydantic import BaseModel


class Signal(BaseModel):
    """Represents a neural signal in the brain."""

    id: str
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    origin: Optional[str] = None
    metadata: Dict[str, Any] = {}


class SignalHandler(BaseModel):
    """Represents a signal processing unit."""

    id: str
    signal_type: str
    processor: Callable
    priority: int = 0
    metadata: Dict[str, Any] = {}


class Synapse:
    """
    Brain's communication system for neural signal processing.
    Manages signal transmission, routing, and coordination between brain components.
    """

    def __init__(self):
        """Initialize the synaptic system."""
        self.processors: Dict[str, List[SignalHandler]] = {}
        self.signal_history: List[Signal] = []
        self.max_history = 1000
        self._active_signals: Set[str] = set()

    def connect(
        self,
        signal_type: str,
        processor: Callable,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Connect a processor to handle specific signal types.

        Args:
            signal_type: Type of signal to process
            processor: Function to process the signal
            priority: Processor priority (higher = earlier)
            metadata: Optional processor metadata

        Returns:
            Processor ID
        """
        processor_id = f"processor_{len(self.processors.get(signal_type, []))}"

        signal_handler = SignalHandler(
            id=processor_id,
            signal_type=signal_type,
            processor=processor,
            priority=priority,
            metadata=metadata or {},
        )

        if signal_type not in self.processors:
            self.processors[signal_type] = []

        self.processors[signal_type].append(signal_handler)

        # Sort processors by priority
        self.processors[signal_type].sort(key=lambda h: h.priority, reverse=True)

        return processor_id

    def disconnect(self, signal_type: str, processor_id: str):
        """
        Disconnect a signal processor.

        Args:
            signal_type: Type of signal
            processor_id: ID of processor to disconnect
        """
        if signal_type in self.processors:
            self.processors[signal_type] = [
                p for p in self.processors[signal_type] if p.id != processor_id
            ]

    def transmit(
        self,
        signal_type: str,
        data: Dict[str, Any],
        origin: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Transmit a signal to connected processors.

        Args:
            signal_type: Type of signal to transmit
            data: Signal data
            origin: Optional signal origin
            metadata: Optional signal metadata

        Returns:
            Result from processors (if any)
        """
        signal = Signal(
            id=f"signal_{len(self.signal_history)}",
            type=signal_type,
            data=data,
            timestamp=datetime.now(),
            origin=origin,
            metadata=metadata or {},
        )

        # Prevent signal loops
        if signal.id in self._active_signals:
            raise ValueError(f"Signal loop detected for {signal_type}")

        self._active_signals.add(signal.id)

        try:
            # Record in history
            self.signal_history.append(signal)
            if len(self.signal_history) > self.max_history:
                self.signal_history.pop(0)

            # Get connected processors
            processors = self.processors.get(signal_type, [])
            if not processors:
                return None

            # Process signal
            results = []
            for processor in processors:
                try:
                    result = processor.processor(signal.data)
                    results.append(result)
                except Exception as e:
                    # Transmit error signal
                    self.transmit(
                        "error",
                        {"error": str(e), "signal": signal.dict(), "processor": processor.dict()},
                    )

            # Return last non-None result
            for result in reversed(results):
                if result is not None:
                    return result
            return None

        finally:
            self._active_signals.remove(signal.id)

    def get_signal_history(
        self, signal_type: Optional[str] = None, limit: int = 10
    ) -> List[Signal]:
        """
        Get recent signal history.

        Args:
            signal_type: Optional type to filter by
            limit: Maximum signals to return

        Returns:
            List of recent signals
        """
        if signal_type:
            signals = [s for s in self.signal_history if s.type == signal_type]
        else:
            signals = self.signal_history.copy()

        return signals[-limit:]

    def get_processors(self, signal_type: Optional[str] = None) -> Dict[str, List[SignalHandler]]:
        """
        Get connected processors.

        Args:
            signal_type: Optional type to filter by

        Returns:
            Dict of processors by signal type
        """
        if signal_type:
            return {signal_type: self.processors.get(signal_type, [])}
        return self.processors.copy()

    def cleanup(self):
        """Clean up synaptic resources."""
        # Clear processors
        self.processors.clear()

        # Clear history
        self.signal_history.clear()

        # Clear active signals
        self._active_signals.clear()


# Example usage:
"""
# Initialize synaptic system
synapse = Synapse()

# Connect signal processor
def process_message(data):
    print(f"Processing signal: {data}")

synapse.connect("message", process_message)

# Transmit signal
synapse.transmit(
    "message",
    {"content": "Hello brain!"}
)

# Clean up
synapse.cleanup()
"""
