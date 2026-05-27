"""
Módulo de estruturas de grafos.

Exporta as classes principais para trabalhar com grafos.
"""

from .edge import Edge
from .abstract_graph import AbstractGraph
from .adjacency_list_graph import AdjacencyListGraph
from .adjacency_matrix_graph import AdjacencyMatrixGraph
from .algorithms import GraphAlgorithms

__all__ = [
    "Edge",
    "AbstractGraph",
    "AdjacencyListGraph",
    "AdjacencyMatrixGraph",
    "GraphAlgorithms",
]
