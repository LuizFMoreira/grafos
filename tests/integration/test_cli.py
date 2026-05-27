"""
Testes para CLI (main.py).

Testa a interface de linha de comando com dados mockados.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from codigos.app.main import setup_argument_parser, main
from codigos.models import User, Issue, PullRequest, Review, Comment, CollaborationGraph


class TestCLI:
    """Testes para CLI."""

    def test_argument_parser_basic(self):
        """Testa parser com argumentos básicos."""
        parser = setup_argument_parser()
        args = parser.parse_args([
            '--owner', 'pytorch',
            '--repo', 'pytorch',
            '--token', 'ghp_test123',
        ])

        assert args.owner == 'pytorch'
        assert args.repo == 'pytorch'
        assert args.token == 'ghp_test123'
        assert args.output == './results'
        assert args.impl == 'list'

    def test_argument_parser_with_options(self):
        """Testa parser com opções customizadas."""
        parser = setup_argument_parser()
        args = parser.parse_args([
            '--owner', 'torvalds',
            '--repo', 'linux',
            '--token', 'token',
            '--output', '/tmp/results',
            '--format', 'csv,gexf',
            '--impl', 'matrix',
            '--verbose',
        ])

        assert args.output == '/tmp/results'
        assert args.format == 'csv,gexf'
        assert args.impl == 'matrix'
        assert args.verbose is True

    def test_argument_parser_missing_required(self):
        """Testa que argumentos obrigatórios são requeridos."""
        parser = setup_argument_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(['--owner', 'pytorch'])

    @patch('codigos.app.main.DataTransformer')
    @patch('codigos.app.main.GraphBuilderService')
    @patch('codigos.app.main.MetricsService')
    @patch('codigos.app.main.CSVExporter')
    def test_main_with_csv_export(
        self,
        mock_csv_exporter,
        mock_metrics,
        mock_builder,
        mock_transformer,
    ):
        """Testa main() com exportação CSV."""
        # Setup mocks
        users = [
            User(id=1, login='alice'),
            User(id=2, login='bob'),
        ]

        now = datetime.now()
        collab_graph = CollaborationGraph(
            repository='test/repo',
            users=users,
            mined_at=now,
        )

        mock_transformer_instance = MagicMock()
        mock_transformer_instance.mine_repository.return_value = collab_graph
        mock_transformer.return_value = mock_transformer_instance

        mock_graph = MagicMock()
        mock_graph.get_vertex_count.return_value = 2
        mock_graph.get_edge_count.return_value = 1

        mock_builder_instance = MagicMock()
        mock_builder_instance.build_all_graphs.return_value = {
            'total': mock_graph,
            'issues': mock_graph,
            'pull_requests': mock_graph,
        }
        mock_builder.return_value = mock_builder_instance

        from codigos.models import MetricsResult
        mock_metrics_instance = MagicMock()
        mock_metrics_instance.calculate_all_metrics.return_value = [
            MetricsResult(user=users[0], pagerank=0.5),
            MetricsResult(user=users[1], pagerank=0.5),
        ]
        mock_metrics_instance.get_metrics_summary.return_value = {
            'avg_pagerank': 0.5,
            'avg_degree_centrality': 0.5,
        }
        mock_metrics_instance.get_top_by_metric.return_value = [
            (users[0], 0.5),
            (users[1], 0.5),
        ]
        mock_metrics.return_value = mock_metrics_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            args = [
                '--owner', 'test',
                '--repo', 'repo',
                '--token', 'token',
                '--output', tmpdir,
                '--format', 'csv',
            ]

            result = main(args)

            # Deve retornar sucesso
            assert result == 0

            # Verificar que transformer foi chamado
            mock_transformer_instance.mine_repository.assert_called_once()

            # Verificar que builder foi chamado
            mock_builder_instance.build_all_graphs.assert_called_once()

            # Verificar que metrics foi calculado
            mock_metrics_instance.calculate_all_metrics.assert_called_once()

    @patch('codigos.app.main.DataTransformer')
    def test_main_handles_mining_error(self, mock_transformer):
        """Testa que main() trata erros de mineração."""
        mock_transformer_instance = MagicMock()
        mock_transformer_instance.mine_repository.side_effect = Exception('API Error')
        mock_transformer.return_value = mock_transformer_instance

        args = [
            '--owner', 'test',
            '--repo', 'repo',
            '--token', 'token',
        ]

        result = main(args)

        # Deve retornar erro
        assert result == 1

    def test_main_keyboard_interrupt(self):
        """Testa que main() trata Ctrl+C."""
        with patch('codigos.app.main.setup_argument_parser') as mock_parser:
            mock_parser.return_value.parse_args.side_effect = KeyboardInterrupt()

            result = main([])

            # Deve retornar 130 (código padrão para SIGINT)
            assert result == 130

    @patch('codigos.app.main.DataTransformer')
    @patch('codigos.app.main.GraphBuilderService')
    @patch('codigos.app.main.MetricsService')
    @patch('codigos.app.main.CSVExporter')
    @patch('codigos.app.main.GEXFExporter')
    @patch('codigos.app.main.GraphMLExporter')
    def test_main_all_formats(
        self,
        mock_graphml,
        mock_gexf,
        mock_csv,
        mock_metrics,
        mock_builder,
        mock_transformer,
    ):
        """Testa exportação em todos os formatos."""
        from codigos.models import MetricsResult

        users = [User(id=1, login='alice')]
        now = datetime.now()
        collab_graph = CollaborationGraph(
            repository='test/repo',
            users=users,
            mined_at=now,
        )

        mock_transformer_instance = MagicMock()
        mock_transformer_instance.mine_repository.return_value = collab_graph
        mock_transformer.return_value = mock_transformer_instance

        mock_graph = MagicMock()
        mock_graph.get_vertex_count.return_value = 1
        mock_graph.get_edge_count.return_value = 0

        mock_builder_instance = MagicMock()
        mock_builder_instance.build_all_graphs.return_value = {
            'total': mock_graph,
            'issues': mock_graph,
            'pull_requests': mock_graph,
        }
        mock_builder.return_value = mock_builder_instance

        mock_metrics_instance = MagicMock()
        mock_metrics_instance.calculate_all_metrics.return_value = [
            MetricsResult(user=users[0], pagerank=1.0),
        ]
        mock_metrics_instance.get_metrics_summary.return_value = {
            'avg_pagerank': 1.0,
            'avg_degree_centrality': 0.0,
        }
        mock_metrics_instance.get_top_by_metric.return_value = [(users[0], 1.0)]
        mock_metrics.return_value = mock_metrics_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            args = [
                '--owner', 'test',
                '--repo', 'repo',
                '--token', 'token',
                '--output', tmpdir,
                '--format', 'csv,gexf,graphml',
            ]

            result = main(args)

            assert result == 0

            # Verificar que todos os exportadores foram chamados
            assert mock_csv.return_value.export.called
            assert mock_gexf.return_value.export.called
            assert mock_graphml.return_value.export.called
