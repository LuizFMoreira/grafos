"""
Testes de integração: pipeline completo de análise.

Testa o fluxo ponta-a-ponta do sistema:
mineração → grafos → métricas → exportação
"""

import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from codigos.models import (
    User,
    Issue,
    PullRequest,
    Review,
    Comment,
    CollaborationGraph,
)
from codigos.github_miner import GithubClient, DataTransformer
from codigos.services import GraphBuilderService, MetricsService
from codigos.exporters import CSVExporter, GEXFExporter, GraphMLExporter


class TestIntegrationPipeline:
    """Testes de integração do pipeline completo."""

    @pytest.fixture
    def sample_collaboration_graph(self):
        """Cria grafo de colaboração de amostra."""
        users = [
            User(id=1, login="alice"),
            User(id=2, login="bob"),
            User(id=3, login="charlie"),
        ]

        now = datetime.now()

        issues = [
            Issue(
                number=1,
                title="Bug fix",
                author=users[0],
                created_at=now,
                updated_at=now,
                url="https://github.com/owner/repo/issues/1",
                state="open",
            ),
        ]

        pull_requests = [
            PullRequest(
                number=1,
                title="Feature",
                author=users[1],
                created_at=now,
                updated_at=now,
                merged_at=now,
                merged_by=users[0],
                url="https://github.com/owner/repo/pull/1",
                state="merged",
            ),
        ]

        reviews = [
            Review(
                id=1,
                author=users[2],
                pr_number=1,
                state="APPROVED",
                submitted_at=now,
                url="https://github.com/owner/repo/pull/1#review-1",
            ),
        ]

        comments = [
            Comment(
                id=1,
                author=users[1],
                body="Good point",
                created_at=now,
                updated_at=now,
                url="https://github.com/owner/repo/issues/1#comment-1",
                issue_number=1,
            ),
            Comment(
                id=2,
                author=users[2],
                body="LGTM",
                created_at=now,
                updated_at=now,
                url="https://github.com/owner/repo/pull/1#comment-2",
                pr_number=1,
            ),
        ]

        return CollaborationGraph(
            repository="owner/repo",
            users=users,
            issues=issues,
            pull_requests=pull_requests,
            reviews=reviews,
            comments=comments,
            mined_at=now,
        )

    def test_full_pipeline_graph_builder_to_export(self, sample_collaboration_graph):
        """Testa pipeline completo: grafo → métricas → export."""
        graph_data = sample_collaboration_graph

        # 1. Construir grafo
        builder = GraphBuilderService(use_adjacency_list=True)
        graph = builder.build_collaboration_graph(graph_data)

        assert graph.get_vertex_count() == 3
        assert graph.get_edge_count() > 0

        # 2. Calcular métricas
        metrics_service = MetricsService(graph, graph_data.users)
        all_metrics = metrics_service.calculate_all_metrics()

        assert len(all_metrics) == 3
        for metric in all_metrics:
            assert metric.pagerank > 0
            assert 0 <= metric.degree_centrality <= 1

        # 3. Exportar
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test")
            csv_exporter = CSVExporter(graph, all_metrics)
            csv_exporter.export(csv_path)

            # Verificar arquivos criados
            assert os.path.exists(f"{csv_path}_nodes.csv")
            assert os.path.exists(f"{csv_path}_edges.csv")

    def test_pipeline_with_different_graph_implementations(self, sample_collaboration_graph):
        """Testa pipeline com ambas implementações de grafo."""
        graph_data = sample_collaboration_graph

        for use_list in [True, False]:
            builder = GraphBuilderService(use_adjacency_list=use_list)
            graph = builder.build_collaboration_graph(graph_data)

            # Mesmos resultados com ambas implementações
            assert graph.get_vertex_count() == 3

            metrics_service = MetricsService(graph, graph_data.users)
            all_metrics = metrics_service.calculate_all_metrics()

            assert len(all_metrics) == 3

            # PageRank deve ser similar (não exato por diferenças numéricas)
            assert all(m.pagerank > 0 for m in all_metrics)

    def test_pipeline_exports_all_formats(self, sample_collaboration_graph):
        """Testa que pipeline pode exportar em todos os formatos."""
        graph_data = sample_collaboration_graph

        builder = GraphBuilderService()
        graph = builder.build_collaboration_graph(graph_data)

        metrics_service = MetricsService(graph, graph_data.users)
        all_metrics = metrics_service.calculate_all_metrics()

        with tempfile.TemporaryDirectory() as tmpdir:
            # CSV
            csv_path = os.path.join(tmpdir, "test")
            CSVExporter(graph, all_metrics).export(csv_path)
            assert os.path.exists(f"{csv_path}_nodes.csv")

            # GEXF
            gexf_path = os.path.join(tmpdir, "test.gexf")
            GEXFExporter(graph, all_metrics).export(gexf_path)
            assert os.path.exists(gexf_path)

            # GraphML
            graphml_path = os.path.join(tmpdir, "test.graphml")
            GraphMLExporter(graph, all_metrics).export(graphml_path)
            assert os.path.exists(graphml_path)

    def test_pipeline_handles_empty_interactions(self):
        """Testa pipeline com grafo vazio (sem interações)."""
        users = [
            User(id=1, login="alice"),
            User(id=2, login="bob"),
        ]

        graph_data = CollaborationGraph(
            repository="owner/repo",
            users=users,
            issues=[],
            pull_requests=[],
            reviews=[],
            comments=[],
            mined_at=datetime.now(),
        )

        builder = GraphBuilderService()
        graph = builder.build_collaboration_graph(graph_data)

        # Deve criar grafo vazio mas válido
        assert graph.get_vertex_count() == 2
        assert graph.get_edge_count() == 0

        # Métricas devem funcionar
        metrics_service = MetricsService(graph, users)
        all_metrics = metrics_service.calculate_all_metrics()
        assert len(all_metrics) == 2

    def test_pipeline_statistics_summary(self, sample_collaboration_graph):
        """Testa que pipeline gera sumário de estatísticas."""
        graph_data = sample_collaboration_graph

        builder = GraphBuilderService()
        graph = builder.build_collaboration_graph(graph_data)

        stats = GraphBuilderService.get_graph_statistics(graph)

        assert 'vertices' in stats
        assert 'edges' in stats
        assert 'density' in stats
        assert stats['vertices'] == 3

        metrics_service = MetricsService(graph, graph_data.users)
        summary = metrics_service.get_metrics_summary()

        assert 'avg_pagerank' in summary
        assert 'max_pagerank' in summary
        assert summary['avg_pagerank'] > 0

    def test_pipeline_handles_self_loops_correctly(self):
        """Testa que pipeline filtra self-loops automaticamente."""
        users = [
            User(id=1, login="alice"),
            User(id=2, login="bob"),
        ]

        now = datetime.now()

        # Comentário do Alice em issue dela mesma (self-loop)
        comments = [
            Comment(
                id=1,
                author=users[0],  # Alice comentando em sua própria issue
                body="Self comment",
                created_at=now,
                updated_at=now,
                url="https://github.com/owner/repo/issues/1#comment-1",
                issue_number=1,
            ),
        ]

        issues = [
            Issue(
                number=1,
                title="Issue by Alice",
                author=users[0],  # Alice é autora
                created_at=now,
                updated_at=now,
                url="https://github.com/owner/repo/issues/1",
            ),
        ]

        graph_data = CollaborationGraph(
            repository="owner/repo",
            users=users,
            issues=issues,
            comments=comments,
            pull_requests=[],
            reviews=[],
            mined_at=now,
        )

        builder = GraphBuilderService()
        graph = builder.build_collaboration_graph(graph_data)

        # Não deve ter self-loop (0 → 0)
        assert not graph.has_edge(0, 0)
        # Grafo deve estar vazio pois só tem self-loop
        assert graph.get_edge_count() == 0

    def test_pipeline_builds_all_three_graphs(self, sample_collaboration_graph):
        """Testa que builder cria corretamente os 3 grafos distintos."""
        graph_data = sample_collaboration_graph

        builder = GraphBuilderService()
        graphs = builder.build_all_graphs(graph_data)

        assert 'total' in graphs
        assert 'issues' in graphs
        assert 'pull_requests' in graphs

        # Total deve ter mais arestas que os parciais
        total_edges = graphs['total'].get_edge_count()
        issues_edges = graphs['issues'].get_edge_count()
        pr_edges = graphs['pull_requests'].get_edge_count()

        assert total_edges >= max(issues_edges, pr_edges)

        # Todos devem ter mesmo número de vértices
        for graph in graphs.values():
            assert graph.get_vertex_count() == 3

    def test_pipeline_metrics_ranking(self, sample_collaboration_graph):
        """Testa que rankings de métricas funcionam no pipeline."""
        graph_data = sample_collaboration_graph

        builder = GraphBuilderService()
        graph = builder.build_collaboration_graph(graph_data)

        metrics_service = MetricsService(graph, graph_data.users)

        # Ranking por PageRank
        top_pagerank = metrics_service.get_top_by_metric('pagerank', top_n=2)
        assert len(top_pagerank) == 2
        assert top_pagerank[0][1] >= top_pagerank[1][1]  # Ordenado descrescente

        # Ranking por degree centrality
        top_degree = metrics_service.get_top_by_metric('degree_centrality', top_n=2)
        assert len(top_degree) == 2
