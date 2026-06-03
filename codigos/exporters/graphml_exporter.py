"""
Exportador GraphML para grafos (formato XML alternativo).

Gera arquivo GraphML para compatibilidade com ferramentas diversas.
"""

from datetime import datetime

from .base_exporter import BaseExporter
from ..models import MetricsResult
from ..core.graph import AbstractGraph


class GraphMLExporter(BaseExporter):
    """Exporta grafo para formato GraphML (XML).

    GraphML (Graph Markup Language) é formato alternativo ao GEXF:
    - Mais amplamente suportado
    - Compatível com Gephi, Cytoscape, yEd, etc
    - Mais simples que GEXF
    - Ideal para compatibilidade máxima
    """

    def export(self, filepath: str) -> None:
        """Exporta grafo para GraphML.

        Args:
            filepath: Caminho completo (com extensão .graphml)

        Raises:
            IOError: Se erro ao escrever arquivo
        """
        if not filepath.endswith('.graphml'):
            filepath = f"{filepath}.graphml"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self._generate_graphml())

    def _generate_graphml(self) -> str:
        """Gera conteúdo GraphML como string.

        Returns:
            String com conteúdo GraphML válido
        """
        lines = []

        # Header XML
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append(
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlschema/graphml" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        )

        # Keys (atributos globais)
        lines.append('  <key id="d0" for="node" attr.name="label" attr.type="string" />')
        lines.append('  <key id="d1" for="node" attr.name="degree_centrality" attr.type="float" />')
        lines.append('  <key id="d2" for="node" attr.name="in_degree" attr.type="int" />')
        lines.append('  <key id="d3" for="node" attr.name="out_degree" attr.type="int" />')
        lines.append('  <key id="d4" for="node" attr.name="betweenness_centrality" attr.type="float" />')
        lines.append('  <key id="d5" for="node" attr.name="closeness_centrality" attr.type="float" />')
        lines.append('  <key id="d6" for="node" attr.name="pagerank" attr.type="float" />')
        lines.append('  <key id="d7" for="node" attr.name="clustering_coefficient" attr.type="float" />')
        lines.append('  <key id="d8" for="node" attr.name="eigenvector_centrality" attr.type="float" />')
        lines.append('  <key id="d9" for="node" attr.name="user_id" attr.type="int" />')
        lines.append('  <key id="d10" for="edge" attr.name="weight" attr.type="float" />')

        # Grafo
        lines.append('  <graph id="G" edgedefault="directed">')

        # Nós
        for vertex_idx in range(self.graph.get_vertex_count()):
            node_data = self._get_node_data(vertex_idx)
            lines.append(self._generate_node_xml(vertex_idx, node_data))

        # Arestas
        edge_id = 0
        for u in range(self.graph.get_vertex_count()):
            for v in range(self.graph.get_vertex_count()):
                if self.graph.has_edge(u, v):
                    edge_data = self._get_edge_data(u, v)
                    lines.append(self._generate_edge_xml(edge_id, edge_data))
                    edge_id += 1

        lines.append('  </graph>')
        lines.append('</graphml>')

        return '\n'.join(lines)

    def _generate_node_xml(self, vertex_idx: int, node_data: dict) -> str:
        """Gera XML de um nó.

        Args:
            vertex_idx: Índice do vértice
            node_data: Dict com dados do nó

        Returns:
            String com XML do nó
        """
        lines = []

        lines.append(f'    <node id="n{vertex_idx}">')

        # Atributos do nó
        lines.append(f'      <data key="d0">{node_data["label"]}</data>')
        lines.append(f'      <data key="d1">{node_data["degree_centrality"]}</data>')
        lines.append(f'      <data key="d2">{node_data["in_degree"]}</data>')
        lines.append(f'      <data key="d3">{node_data["out_degree"]}</data>')
        lines.append(f'      <data key="d4">{node_data["betweenness_centrality"]}</data>')
        lines.append(f'      <data key="d5">{node_data["closeness_centrality"]}</data>')
        lines.append(f'      <data key="d6">{node_data["pagerank"]}</data>')
        lines.append(f'      <data key="d7">{node_data["clustering_coefficient"]}</data>')
        lines.append(f'      <data key="d8">{node_data["eigenvector_centrality"]}</data>')
        lines.append(f'      <data key="d9">{node_data["user_id"]}</data>')

        lines.append('    </node>')

        return '\n'.join(lines)

    def _generate_edge_xml(self, edge_id: int, edge_data: dict) -> str:
        """Gera XML de uma aresta.

        Args:
            edge_id: ID da aresta (sequencial)
            edge_data: Dict com dados da aresta

        Returns:
            String com XML da aresta
        """
        source = edge_data['source']
        target = edge_data['target']
        weight = edge_data['weight']

        return (
            f'    <edge id="e{edge_id}" source="n{source}" target="n{target}">\n'
            f'      <data key="d10">{weight}</data>\n'
            f'    </edge>'
        )
