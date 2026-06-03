"""
Exportador GEXF para grafos (formato XML Gephi).

Gera arquivo GEXF com nós, arestas e atributos para Gephi.
"""

from typing import Optional
from datetime import datetime

from .base_exporter import BaseExporter
from ..models import MetricsResult
from ..core.graph import AbstractGraph


class GEXFExporter(BaseExporter):
    """Exporta grafo para formato GEXF (XML).

    GEXF (Graph Exchange XML Format) é formato estruturado que suporta:
    - Nós com atributos
    - Arestas ponderadas
    - Metadados do grafo
    - Validação de esquema

    Ideal para Gephi e ferramentas especializadas em grafos.
    """

    def export(self, filepath: str) -> None:
        """Exporta grafo para GEXF.

        Args:
            filepath: Caminho completo (com extensão .gexf)

        Raises:
            IOError: Se erro ao escrever arquivo
        """
        if not filepath.endswith('.gexf'):
            filepath = f"{filepath}.gexf"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self._generate_gexf())

    def _generate_gexf(self) -> str:
        """Gera conteúdo GEXF como string.

        Returns:
            String com conteúdo GEXF válido
        """
        lines = []

        # Header XML
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append(
            '<gexf xmlns="http://www.gexf.net/1.2draft" '
            'version="1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        )

        # Meta
        lines.append('  <meta lastmodifieddate="' + datetime.now().isoformat() + '">')
        lines.append('    <creator>GraphAnalyzer v1.0</creator>')
        lines.append('    <description>GitHub Collaboration Network</description>')
        lines.append('  </meta>')

        # Grafo
        lines.append('  <graph mode="static" defaultedgetype="directed">')

        # Atributos (dinâmico)
        lines.append('    <attributes class="node">')
        attributes = [
            ('degree_centrality', 'float'),
            ('in_degree', 'integer'),
            ('out_degree', 'integer'),
            ('betweenness_centrality', 'float'),
            ('closeness_centrality', 'float'),
            ('pagerank', 'float'),
            ('clustering_coefficient', 'float'),
            ('eigenvector_centrality', 'float'),
            ('user_id', 'integer'),
        ]

        for attr_id, (attr_name, attr_type) in enumerate(attributes):
            lines.append(
                f'      <attribute id="{attr_id}" title="{attr_name}" '
                f'type="{attr_type}" />'
            )

        lines.append('    </attributes>')

        # Atributos de arestas
        lines.append('    <attributes class="edge">')
        lines.append('      <attribute id="0" title="weight" type="float" />')
        lines.append('    </attributes>')

        # Nós
        lines.append('    <nodes>')
        for vertex_idx in range(self.graph.get_vertex_count()):
            node_data = self._get_node_data(vertex_idx)
            lines.append(self._generate_node_xml(vertex_idx, node_data))
        lines.append('    </nodes>')

        # Arestas
        lines.append('    <edges>')
        edge_id = 0
        for u in range(self.graph.get_vertex_count()):
            for v in range(self.graph.get_vertex_count()):
                if self.graph.has_edge(u, v):
                    edge_data = self._get_edge_data(u, v)
                    lines.append(self._generate_edge_xml(edge_id, edge_data))
                    edge_id += 1
        lines.append('    </edges>')

        lines.append('  </graph>')
        lines.append('</gexf>')

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

        lines.append(f'      <node id="{vertex_idx}" label="{node_data["label"]}">')
        lines.append('        <attvalues>')

        # Mapeia dados para atributos
        attr_mapping = [
            (0, 'degree_centrality'),
            (1, 'in_degree'),
            (2, 'out_degree'),
            (3, 'betweenness_centrality'),
            (4, 'closeness_centrality'),
            (5, 'pagerank'),
            (6, 'clustering_coefficient'),
            (7, 'eigenvector_centrality'),
            (8, 'user_id'),
        ]

        for attr_id, attr_name in attr_mapping:
            value = node_data.get(attr_name, 0)
            lines.append(f'          <attvalue for="{attr_id}" value="{value}" />')

        lines.append('        </attvalues>')
        lines.append('      </node>')

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
            f'      <edge id="{edge_id}" source="{source}" '
            f'target="{target}" weight="{weight}">\n'
            f'        <attvalues>\n'
            f'          <attvalue for="0" value="{weight}" />\n'
            f'        </attvalues>\n'
            f'      </edge>'
        )
