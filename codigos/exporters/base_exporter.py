"""
Classe base para exportadores de grafos.

Define a interface comum para todos os exportadores.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from ..models import MetricsResult
from ..core.graph import AbstractGraph


class BaseExporter(ABC):
    """Classe base abstrata para exportadores de grafos.

    Define a interface que todos os exportadores devem implementar.
    Exportadores convertam grafos e métricas em diferentes formatos.
    """

    def __init__(self, graph: AbstractGraph, metrics: List[MetricsResult]):
        """Inicializa exportador.

        Args:
            graph: Grafo a exportar
            metrics: Lista de MetricsResult (um por usuário)

        Raises:
            ValueError: Se tamanhos não correspondem
        """
        if len(metrics) != graph.get_vertex_count():
            raise ValueError(
                f"Graph has {graph.get_vertex_count()} vertices "
                f"but {len(metrics)} metrics provided"
            )

        self.graph = graph
        self.metrics = metrics

    @abstractmethod
    def export(self, filepath: str) -> None:
        """Exporta grafo para arquivo.

        Args:
            filepath: Caminho do arquivo (sem extensão, será adicionada)

        Raises:
            IOError: Se erro ao escrever arquivo
        """
        pass

    def _get_node_data(self, vertex_index: int) -> Dict[str, Any]:
        """Retorna dados de um nó para exportação.

        Args:
            vertex_index: Índice do vértice

        Returns:
            Dict com dados do nó (id, label, métricas, etc)
        """
        metric = self.metrics[vertex_index]

        return {
            'id': vertex_index,
            'label': metric.user.login,
            'user_id': metric.user.id,
            'degree_centrality': metric.degree_centrality,
            'in_degree': metric.in_degree,
            'out_degree': metric.out_degree,
            'betweenness_centrality': metric.betweenness_centrality,
            'closeness_centrality': metric.closeness_centrality,
            'pagerank': metric.pagerank,
            'clustering_coefficient': metric.clustering_coefficient,
            'eigenvector_centrality': metric.eigenvector_centrality,
        }

    def _get_edge_data(self, u: int, v: int) -> Dict[str, Any]:
        """Retorna dados de uma aresta para exportação.

        Args:
            u: Vértice origem
            v: Vértice destino

        Returns:
            Dict com dados da aresta (source, target, weight)
        """
        return {
            'source': u,
            'target': v,
            'weight': self.graph.get_edge_weight(u, v),
        }
