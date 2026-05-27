"""
Testes para GraphBuilderService.

Testa construção de grafos a partir de dados colaborativos.
"""

import pytest
from datetime import datetime

from codigos.models import (
    User,
    Issue,
    PullRequest,
    Review,
    Comment,
    CollaborationGraph,
)
from codigos.services import GraphBuilderService
from codigos.core.graph import AdjacencyListGraph, AdjacencyMatrixGraph
from codigos.exceptions.mining_exceptions import GithubMiningError


class TestGraphBuilderService:
    """Testes para GraphBuilderService."""

    @pytest.fixture
    def users(self):
        """Cria usuários para testes."""
        return [
            User(id=1, login="alice"),
            User(id=2, login="bob"),
            User(id=3, login="charlie"),
        ]

    @pytest.fixture
    def collaboration_graph(self, users):
        """Cria CollaborationGraph de teste."""
        alice, bob, charlie = users

        now = datetime.now()

        issues = [
            Issue(
                number=1,
                title="Bug fix",
                author=alice,
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
                author=bob,
                created_at=now,
                updated_at=now,
                url="https://github.com/owner/repo/pull/1",
                merged_at=now,
                merged_by=alice,
                state="merged",
            ),
        ]

        reviews = [
            Review(
                id=1,
                author=charlie,
                pr_number=1,
                state="APPROVED",
                submitted_at=now,
                url="https://github.com/owner/repo/pull/1#review-1",
            ),
        ]

        comments = [
            Comment(
                id=1,
                author=bob,
                body="Good catch!",
                created_at=now,
                updated_at=now,
                url="https://github.com/owner/repo/issues/1#comment-1",
                issue_number=1,
            ),
            Comment(
                id=2,
                author=charlie,
                body="Looks good",
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

    def test_init_adjacency_list(self):
        """Cria builder com AdjacencyListGraph."""
        builder = GraphBuilderService(use_adjacency_list=True)
        assert builder.use_adjacency_list is True

    def test_init_adjacency_matrix(self):
        """Cria builder com AdjacencyMatrixGraph."""
        builder = GraphBuilderService(use_adjacency_list=False)
        assert builder.use_adjacency_list is False

    def test_build_collaboration_graph(self, collaboration_graph):
        """Constrói grafo completo de colaboração."""
        builder = GraphBuilderService(use_adjacency_list=True)
        graph = builder.build_collaboration_graph(collaboration_graph)

        assert isinstance(graph, AdjacencyListGraph)
        assert graph.get_vertex_count() == 3
        assert graph.get_edge_count() > 0

    def test_build_collaboration_graph_with_matrix(self, collaboration_graph):
        """Constrói grafo com AdjacencyMatrixGraph."""
        builder = GraphBuilderService(use_adjacency_list=False)
        graph = builder.build_collaboration_graph(collaboration_graph)

        assert isinstance(graph, AdjacencyMatrixGraph)
        assert graph.get_vertex_count() == 3

    def test_build_collaboration_graph_no_users(self):
        """Rejeita se não há usuários."""
        builder = GraphBuilderService()
        graph = CollaborationGraph(repository="owner/repo", users=[])

        with pytest.raises(GithubMiningError):
            builder.build_collaboration_graph(graph)

    def test_user_labels(self, collaboration_graph):
        """Verifica se rótulos de usuários são adicionados."""
        builder = GraphBuilderService()
        graph = builder.build_collaboration_graph(collaboration_graph)

        # Usuários são adicionados como rótulos
        for i, user in enumerate(collaboration_graph.users):
            label = graph.get_vertex_label(i)
            assert label == user.login

    def test_build_issues_graph(self, collaboration_graph):
        """Constrói grafo apenas com interações em issues."""
        builder = GraphBuilderService()
        graph = builder.build_issues_graph(collaboration_graph)

        assert graph.get_vertex_count() == 3
        # Deve ter apenas comentário em issue
        assert graph.get_edge_count() >= 1

    def test_build_pull_requests_graph(self, collaboration_graph):
        """Constrói grafo apenas com interações em PRs."""
        builder = GraphBuilderService()
        graph = builder.build_pull_requests_graph(collaboration_graph)

        assert graph.get_vertex_count() == 3
        # Deve ter comentário em PR, review e merge
        assert graph.get_edge_count() >= 1

    def test_build_all_graphs(self, collaboration_graph):
        """Constrói todos os 4 grafos de uma vez."""
        builder = GraphBuilderService()
        graphs = builder.build_all_graphs(collaboration_graph)

        assert "total" in graphs
        assert "issues" in graphs
        assert "pull_requests" in graphs

        # Todos devem ter mesmo número de vértices
        v_count = graphs["total"].get_vertex_count()
        assert graphs["issues"].get_vertex_count() == v_count
        assert graphs["pull_requests"].get_vertex_count() == v_count

    def test_edge_weights_issue_comment(self, users):
        """Verifica peso de comentário em issue."""
        alice, bob, _ = users
        now = datetime.now()

        graph_data = CollaborationGraph(
            repository="owner/repo",
            users=users,
            issues=[
                Issue(
                    number=1,
                    title="Test",
                    author=alice,
                    created_at=now,
                    updated_at=now,
                    url="https://github.com/owner/repo/issues/1",
                ),
            ],
            comments=[
                Comment(
                    id=1,
                    author=bob,
                    body="Comment",
                    created_at=now,
                    updated_at=now,
                    url="https://github.com/owner/repo/issues/1#comment-1",
                    issue_number=1,
                ),
            ],
        )

        builder = GraphBuilderService()
        graph = builder.build_issues_graph(graph_data)

        # Bob (idx 1) → Alice (idx 0)
        assert graph.has_edge(1, 0)
        assert graph.get_edge_weight(1, 0) == 2.0

    def test_edge_weights_pr_review(self, users):
        """Verifica peso de review de PR."""
        alice, bob, charlie = users
        now = datetime.now()

        graph_data = CollaborationGraph(
            repository="owner/repo",
            users=users,
            pull_requests=[
                PullRequest(
                    number=1,
                    title="Test",
                    author=bob,
                    created_at=now,
                    updated_at=now,
                    url="https://github.com/owner/repo/pull/1",
                ),
            ],
            reviews=[
                Review(
                    id=1,
                    author=charlie,
                    pr_number=1,
                    state="APPROVED",
                    submitted_at=now,
                    url="https://github.com/owner/repo/pull/1#review-1",
                ),
            ],
        )

        builder = GraphBuilderService()
        graph = builder.build_pull_requests_graph(graph_data)

        # Charlie (idx 2) → Bob (idx 1)
        assert graph.has_edge(2, 1)
        assert graph.get_edge_weight(2, 1) == 4.0

    def test_edge_weights_pr_merge(self, users):
        """Verifica peso de merge de PR."""
        alice, bob, _ = users
        now = datetime.now()

        graph_data = CollaborationGraph(
            repository="owner/repo",
            users=users,
            pull_requests=[
                PullRequest(
                    number=1,
                    title="Test",
                    author=bob,
                    created_at=now,
                    updated_at=now,
                    merged_at=now,
                    merged_by=alice,
                    url="https://github.com/owner/repo/pull/1",
                    state="merged",
                ),
            ],
        )

        builder = GraphBuilderService()
        graph = builder.build_pull_requests_graph(graph_data)

        # Alice (idx 0) → Bob (idx 1)
        assert graph.has_edge(0, 1)
        assert graph.get_edge_weight(0, 1) == 5.0

    def test_no_self_loops(self, users):
        """Verifica que self-loops não são criados."""
        alice, _, _ = users
        now = datetime.now()

        graph_data = CollaborationGraph(
            repository="owner/repo",
            users=users,
            issues=[
                Issue(
                    number=1,
                    title="Test",
                    author=alice,
                    created_at=now,
                    updated_at=now,
                    url="https://github.com/owner/repo/issues/1",
                ),
            ],
            comments=[
                Comment(
                    id=1,
                    author=alice,  # Mesmo autor da issue
                    body="Self comment",
                    created_at=now,
                    updated_at=now,
                    url="https://github.com/owner/repo/issues/1#comment-1",
                    issue_number=1,
                ),
            ],
        )

        builder = GraphBuilderService()
        graph = builder.build_issues_graph(graph_data)

        # Não deve ter aresta alice → alice
        alice_idx = 0
        assert not graph.has_edge(alice_idx, alice_idx)

    def test_get_graph_statistics(self, collaboration_graph):
        """Retorna estatísticas do grafo."""
        builder = GraphBuilderService()
        graph = builder.build_collaboration_graph(collaboration_graph)

        stats = GraphBuilderService.get_graph_statistics(graph)

        assert "vertices" in stats
        assert "edges" in stats
        assert "max_edges" in stats
        assert "density" in stats
        assert "is_connected" in stats
        assert "is_complete" in stats

        assert stats["vertices"] == 3
        assert stats["max_edges"] == 3 * (3 - 1)
        assert 0 <= stats["density"] <= 1
