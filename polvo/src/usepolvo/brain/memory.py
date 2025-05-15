# brain/memory.py
from datetime import datetime, timedelta
from time import sleep
from typing import Any, Dict, List, Optional

import numpy as np
from pydantic import BaseModel


class MemoryEntry(BaseModel):
    """Represents a single memory in the brain's memory system."""

    id: str
    content: Dict[str, Any]
    timestamp: datetime
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = {}
    importance: float = 1.0
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class Memory:
    """
    Brain's memory system responsible for storing and retrieving information.
    Handles memory formation, recall, and maintenance using importance-based filtering
    and similarity-based retrieval.
    """

    def __init__(self, memory_limit: int = 100):
        """
        Initialize the memory system.

        Args:
            memory_limit: Maximum number of memories to retain
        """
        self.memory_limit = memory_limit
        self.memories: List[MemoryEntry] = []

        # Start memory maintenance
        self._maintenance_task = None

    def store(
        self,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 1.0,
    ) -> str:
        """
        Store new information in memory.

        Args:
            content: Information to store
            metadata: Additional memory metadata
            importance: Memory importance (0-1)

        Returns:
            ID of the stored memory
        """

        # Create memory trace
        memory = MemoryEntry(
            id=f"mem_{len(self.memories)}",
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {},
            importance=importance,
        )

        # Generate neural embedding
        memory.embedding = self._generate_embedding(content)

        # Store memory
        self.memories.append(memory)

        # Maintain memory limit
        self._enforce_capacity()

        return memory.id

    def recall(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Recall a specific memory by ID.

        Args:
            memory_id: ID of memory to recall

        Returns:
            The memory if found, None otherwise
        """

        for memory in self.memories:
            if memory.id == memory_id:
                # Update memory access patterns
                memory.access_count += 1
                memory.last_accessed = datetime.now()
                return memory
        return None

    def recall_relevant(
        self, query: str, limit: int = 5, min_similarity: float = 0.5
    ) -> List[MemoryEntry]:
        """
        Recall memories relevant to a query.

        Args:
            query: Query to match against memories
            limit: Maximum memories to recall
            min_similarity: Minimum similarity threshold

        Returns:
            List of relevant memories
        """
        # Generate query embedding
        query_embedding = self._generate_embedding({"text": query})

        # Calculate memory similarities
        similarities = []
        for memory in self.memories:
            if memory.embedding:
                similarity = self._calculate_similarity(query_embedding, memory.embedding)
                similarities.append((memory, similarity))

        # Sort by similarity and importance
        sorted_memories = sorted(similarities, key=lambda x: x[1] * x[0].importance, reverse=True)

        # Filter and limit results
        relevant_memories = [
            memory for memory, similarity in sorted_memories if similarity >= min_similarity
        ][:limit]

        # Update access patterns
        for memory in relevant_memories:
            memory.access_count += 1
            memory.last_accessed = datetime.now()

        return relevant_memories

    def adjust_importance(self, memory_id: str, importance: float):
        """
        Adjust the importance of a memory.

        Args:
            memory_id: Memory to adjust
            importance: New importance value (0-1)
        """
        memory = self.recall(memory_id)
        if memory:
            memory.importance = max(0.0, min(1.0, importance))

    def forget(self, memory_id: str):
        """
        Actively forget (remove) a memory.

        Args:
            memory_id: Memory to forget
        """
        self.memories = [m for m in self.memories if m.id != memory_id]

    def _enforce_capacity(self):
        """Maintain memory capacity by removing least important memories."""
        if len(self.memories) <= self.memory_limit:
            return

        # Score memories for retention
        scores = []
        for memory in self.memories:
            # Consider recency, importance, and access patterns
            time_factor = 1.0 / (datetime.now() - memory.timestamp).total_seconds()
            access_factor = 1.0 + (0.1 * memory.access_count)

            score = memory.importance * time_factor * access_factor
            scores.append((memory, score))

        # Keep highest scoring memories
        sorted_memories = sorted(scores, key=lambda x: x[1], reverse=True)
        self.memories = [m[0] for m in sorted_memories[: self.memory_limit]]

    def _periodic_maintenance(self):
        """Periodically maintain memory system."""
        while True:
            try:
                # sleep(3600)  # Run hourly
                self._maintain()
            except Exception as e:
                print(f"Memory maintenance error: {e}")

    def _maintain(self):
        """Perform memory system maintenance."""

        # Remove old, unused memories
        cutoff = datetime.now() - timedelta(days=30)
        self.memories = [
            m
            for m in self.memories
            if (m.last_accessed and m.last_accessed > cutoff) or m.importance > 0.8
        ]

    def _generate_embedding(self, content: Dict[str, Any]) -> List[float]:
        """Generate neural embedding for content."""
        # TODO: Implement actual embedding generation
        # For now, return random embedding
        return list(np.random.rand(384))

    def _calculate_similarity(self, embed1: List[float], embed2: List[float]) -> float:
        """Calculate neural similarity between embeddings."""
        a = np.array(embed1)
        b = np.array(embed2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def cleanup(self):
        """Clean up memory system resources."""
        if self._maintenance_task:
            self._maintenance_task.cancel()
            try:
                self._maintenance_task
            except Exception:
                pass
