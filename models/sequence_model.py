"""Data models for GeneStudio."""

from dataclasses import dataclass


@dataclass
class SequenceData:
    """Stores DNA sequence information."""
    header: str
    sequence: str
    
    @property
    def length(self) -> int:
        """Get sequence length."""
        return len(self.sequence)


@dataclass
class MatchResult:
    """Stores pattern matching results."""
    pattern: str
    positions: list[int]
    algorithm: str
    
    @property
    def count(self) -> int:
        """Get number of matches."""
        return len(self.positions)


@dataclass
class GraphData:
    """Stores overlap graph data."""
    adjacency_list: dict
    min_overlap: int
    num_sequences: int
    
    def get_edges(self) -> list[tuple[int, int]]:
        """Get list of edges as (from, to) tuples."""
        edges = []
        for from_node, to_nodes in self.adjacency_list.items():
            for to_node in to_nodes:
                edges.append((from_node, to_node))
        return edges
