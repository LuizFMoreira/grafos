"""
Testes para exportadores de grafos.

Testa CSV, GEXF e GraphML exporters.
"""

import pytest
import os
import csv
import tempfile
import xml.etree.ElementTree as ET

from codigos.models import User, MetricsResult
from codigos.core.graph import AdjacencyListGraph
from codigos.exporters import CSVExporter, GEXFExporter, GraphMLExporter


class TestCSVExporter:
    """Testes para CSVExporter."""

    @pytest.fixture
    def setup(self):
        """Setup para testes."""
        graph = AdjacencyListGraph(3)
        graph.add_edge(0, 1, weight=2.0)
        graph.add_edge(1, 2, weight=3.0)
        graph.add_edge(2, 0, weight=1.0)

        metrics = [
            MetricsResult(
                user=User(id=1, login="alice"),
                degree_centrality=0.5,
                in_degree=1,
                out_degree=1,
                pagerank=0.33,
            ),
            MetricsResult(
                user=User(id=2, login="bob"),
                degree_centrality=0.5,
                in_degree=1,
                out_degree=1,
                pagerank=0.33,
            ),
            MetricsResult(
                user=User(id=3, login="charlie"),
                degree_centrality=0.5,
                in_degree=1,
                out_degree=1,
                pagerank=0.34,
            ),
        ]

        return graph, metrics

    def test_export_creates_files(self, setup):
        """Verifica se export cria arquivos."""
        graph, metrics = setup

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph")
            exporter = CSVExporter(graph, metrics)
            exporter.export(filepath)

            # Verifica se ambos arquivos foram criados
            nodes_file = f"{filepath}_nodes.csv"
            edges_file = f"{filepath}_edges.csv"

            assert os.path.exists(nodes_file)
            assert os.path.exists(edges_file)

    def test_nodes_csv_format(self, setup):
        """Verifica formato de nodes.csv."""
        graph, metrics = setup

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph")
            exporter = CSVExporter(graph, metrics)
            exporter.export(filepath)

            nodes_file = f"{filepath}_nodes.csv"

            with open(nodes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                # Deve ter 3 linhas
                assert len(rows) == 3

                # Verificar headers
                assert 'id' in reader.fieldnames
                assert 'label' in reader.fieldnames
                assert 'pagerank' in reader.fieldnames

                # Verificar dados
                assert rows[0]['label'] == 'alice'
                assert rows[1]['label'] == 'bob'
                assert rows[2]['label'] == 'charlie'

    def test_edges_csv_format(self, setup):
        """Verifica formato de edges.csv."""
        graph, metrics = setup

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph")
            exporter = CSVExporter(graph, metrics)
            exporter.export(filepath)

            edges_file = f"{filepath}_edges.csv"

            with open(edges_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                # Deve ter 3 arestas
                assert len(rows) == 3

                # Verificar headers
                assert 'source' in reader.fieldnames
                assert 'target' in reader.fieldnames
                assert 'weight' in reader.fieldnames

                # Verificar primeiros dados
                assert rows[0]['source'] == '0'
                assert rows[0]['target'] == '1'
                assert float(rows[0]['weight']) == 2.0


class TestGEXFExporter:
    """Testes para GEXFExporter."""

    @pytest.fixture
    def setup(self):
        """Setup para testes."""
        graph = AdjacencyListGraph(2)
        graph.add_edge(0, 1, weight=2.0)

        metrics = [
            MetricsResult(
                user=User(id=1, login="alice"),
                degree_centrality=0.5,
                pagerank=0.5,
            ),
            MetricsResult(
                user=User(id=2, login="bob"),
                degree_centrality=0.5,
                pagerank=0.5,
            ),
        ]

        return graph, metrics

    def test_export_creates_file(self, setup):
        """Verifica se export cria arquivo GEXF."""
        graph, metrics = setup

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph.gexf")
            exporter = GEXFExporter(graph, metrics)
            exporter.export(filepath)

            assert os.path.exists(filepath)

    def test_gexf_valid_xml(self, setup):
        """Verifica se GEXF é XML válido."""
        graph, metrics = setup

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph.gexf")
            exporter = GEXFExporter(graph, metrics)
            exporter.export(filepath)

            # Tenta parsear como XML
            tree = ET.parse(filepath)
            root = tree.getroot()

            # Verifica root element
            assert root.tag.endswith('gexf')

    def test_gexf_has_nodes_and_edges(self, setup):
        """Verifica se GEXF contém nós e arestas."""
        graph, metrics = setup

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph.gexf")
            exporter = GEXFExporter(graph, metrics)
            exporter.export(filepath)

            tree = ET.parse(filepath)
            root = tree.getroot()

            # Namespaces
            ns = {'gexf': 'http://www.gexf.net/1.2draft'}

            # Busca nós
            nodes = root.findall('.//gexf:node', ns)
            assert len(nodes) == 2

            # Busca arestas
            edges = root.findall('.//gexf:edge', ns)
            assert len(edges) == 1


class TestGraphMLExporter:
    """Testes para GraphMLExporter."""

    @pytest.fixture
    def setup(self):
        """Setup para testes."""
        graph = AdjacencyListGraph(2)
        graph.add_edge(0, 1, weight=2.0)

        metrics = [
            MetricsResult(
                user=User(id=1, login="alice"),
                degree_centrality=0.5,
                pagerank=0.5,
            ),
            MetricsResult(
                user=User(id=2, login="bob"),
                degree_centrality=0.5,
                pagerank=0.5,
            ),
        ]

        return graph, metrics

    def test_export_creates_file(self, setup):
        """Verifica se export cria arquivo GraphML."""
        graph, metrics = setup

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph.graphml")
            exporter = GraphMLExporter(graph, metrics)
            exporter.export(filepath)

            assert os.path.exists(filepath)

    def test_graphml_valid_xml(self, setup):
        """Verifica se GraphML é XML válido."""
        graph, metrics = setup

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph.graphml")
            exporter = GraphMLExporter(graph, metrics)
            exporter.export(filepath)

            # Tenta parsear como XML
            tree = ET.parse(filepath)
            root = tree.getroot()

            # Verifica root element
            assert root.tag.endswith('graphml')

    def test_graphml_has_nodes_and_edges(self, setup):
        """Verifica se GraphML contém nós e arestas."""
        graph, metrics = setup

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph.graphml")
            exporter = GraphMLExporter(graph, metrics)
            exporter.export(filepath)

            tree = ET.parse(filepath)
            root = tree.getroot()

            # Namespaces
            ns = {'graphml': 'http://graphml.graphdrawing.org/xmlschema/graphml'}

            # Busca nós
            nodes = root.findall('.//graphml:node', ns)
            assert len(nodes) == 2

            # Busca arestas
            edges = root.findall('.//graphml:edge', ns)
            assert len(edges) == 1

    def test_graphml_edge_has_weight(self, setup):
        """Verifica se arestas em GraphML têm peso."""
        graph, metrics = setup

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph.graphml")
            exporter = GraphMLExporter(graph, metrics)
            exporter.export(filepath)

            tree = ET.parse(filepath)
            root = tree.getroot()

            # Namespaces
            ns = {'graphml': 'http://graphml.graphdrawing.org/xmlschema/graphml'}

            # Busca primeira aresta
            edges = root.findall('.//graphml:edge', ns)
            assert len(edges) > 0

            # Verifica se tem dados de peso
            edge = edges[0]
            data_elements = edge.findall('graphml:data', ns)
            assert len(data_elements) > 0
