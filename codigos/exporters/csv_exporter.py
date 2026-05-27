"""
Exportador CSV para grafos (formato Gephi).

Gera nodes.csv e edges.csv para visualização em Gephi.
"""

import csv
from typing import Optional

from .base_exporter import BaseExporter
from ..models import MetricsResult
from ..core.graph import AbstractGraph


class CSVExporter(BaseExporter):
    """Exporta grafo para formato CSV (Gephi).

    Cria dois arquivos:
    - {filepath}_nodes.csv: nós com métricas
    - {filepath}_edges.csv: arestas com pesos

    Formato Gephi padrão com UTF-8 encoding.
    """

    def export(self, filepath: str) -> None:
        """Exporta grafo para CSV.

        Args:
            filepath: Caminho base (sem extensão)

        Raises:
            IOError: Se erro ao escrever arquivos
        """
        self._export_nodes(filepath)
        self._export_edges(filepath)

    def _export_nodes(self, filepath: str) -> None:
        """Exporta nós para nodes.csv.

        Colunas:
        - id: índice do vértice
        - label: nome do usuário (login)
        - user_id: ID do usuário no GitHub
        - degree_centrality: centralidade de grau
        - in_degree: grau de entrada
        - out_degree: grau de saída
        - betweenness_centrality: centralidade de intermediação
        - closeness_centrality: centralidade de proximidade
        - pagerank: PageRank
        - clustering_coefficient: coeficiente de clustering
        - eigenvector_centrality: centralidade de autovetor

        Args:
            filepath: Caminho base para arquivo nodes.csv
        """
        filename = f"{filepath}_nodes.csv"

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    'id',
                    'label',
                    'user_id',
                    'degree_centrality',
                    'in_degree',
                    'out_degree',
                    'betweenness_centrality',
                    'closeness_centrality',
                    'pagerank',
                    'clustering_coefficient',
                    'eigenvector_centrality',
                ],
                extrasaction='ignore',
            )

            writer.writeheader()

            for vertex_idx in range(self.graph.get_vertex_count()):
                node_data = self._get_node_data(vertex_idx)
                writer.writerow(node_data)

    def _export_edges(self, filepath: str) -> None:
        """Exporta arestas para edges.csv.

        Colunas:
        - source: índice do vértice origem
        - target: índice do vértice destino
        - weight: peso da aresta

        Args:
            filepath: Caminho base para arquivo edges.csv
        """
        filename = f"{filepath}_edges.csv"

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['source', 'target', 'weight'],
                extrasaction='ignore',
            )

            writer.writeheader()

            # Itera sobre todas as arestas do grafo
            for u in range(self.graph.get_vertex_count()):
                for v in range(self.graph.get_vertex_count()):
                    if self.graph.has_edge(u, v):
                        edge_data = self._get_edge_data(u, v)
                        writer.writerow(edge_data)
