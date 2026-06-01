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


class TestPdfAlignedGraphs:
    """Garante que os 3+1 grafos exigidos pelo PDF (Etapa 1) são gerados com
    os pesos corretos e contêm exatamente as arestas esperadas."""

    @pytest.fixture
    def users(self):
        return [
            User(id=1, login="alice"),    # autora da issue
            User(id=2, login="bob"),      # autor do PR
            User(id=3, login="charlie"),  # comenta + revisa
            User(id=4, login="dani"),     # fecha issue alheia
        ]

    @pytest.fixture
    def data(self, users):
        alice, bob, charlie, dani = users
        t = datetime.now()
        issues = [
            Issue(
                number=1, title="bug", author=alice,
                created_at=t, updated_at=t,
                url="u", state="closed",
                closed_by=dani, closed_at=t,
            ),
        ]
        prs = [
            PullRequest(
                number=10, title="feat", author=bob,
                created_at=t, updated_at=t,
                url="u", merged_at=t, merged_by=alice, state="merged",
            ),
        ]
        reviews = [
            Review(id=1, author=charlie, pr_number=10,
                   state="APPROVED", submitted_at=t, url="u"),
        ]
        comments = [
            Comment(id=100, author=charlie, body="x",
                    created_at=t, updated_at=t, url="u", issue_number=1),
            Comment(id=101, author=charlie, body="y",
                    created_at=t, updated_at=t, url="u", pr_number=10),
        ]
        return CollaborationGraph(
            repository="o/r", users=users, issues=issues,
            pull_requests=prs, reviews=reviews, comments=comments,
            mined_at=t,
        )

    def test_comments_graph_has_only_comment_edges(self, data):
        g = GraphBuilderService().build_comments_graph(data)
        # charlie→alice (comentário em issue), charlie→bob (comentário em PR)
        assert g.get_edge_count() == 2
        assert g.has_edge(2, 0) is True  # charlie(idx 2) → alice(idx 0)
        assert g.has_edge(2, 1) is True  # charlie → bob
        assert g.get_edge_weight(2, 0) == pytest.approx(2.0)

    def test_issue_close_graph_only_third_party_closures(self, data):
        g = GraphBuilderService().build_issue_close_graph(data)
        # dani fechou issue de alice → 1 aresta peso 3
        assert g.get_edge_count() == 1
        assert g.has_edge(3, 0) is True  # dani(idx 3) → alice
        assert g.get_edge_weight(3, 0) == pytest.approx(3.0)

    def test_reviews_merges_graph_has_review_and_merge(self, data):
        g = GraphBuilderService().build_reviews_merges_graph(data)
        # charlie revisou PR de bob (peso 4) + alice fez merge do PR de bob (peso 5)
        assert g.get_edge_count() == 2
        assert g.get_edge_weight(2, 1) == pytest.approx(4.0)  # charlie → bob
        assert g.get_edge_weight(0, 1) == pytest.approx(5.0)  # alice → bob

    def test_integrated_graph_accumulates_weights(self, data):
        g = GraphBuilderService().build_integrated_graph(data)
        # charlie → bob ocorre via comentário (2) e via review (4) → 6
        assert g.get_edge_weight(2, 1) == pytest.approx(6.0)
        # alice → bob é só do merge (5)
        assert g.get_edge_weight(0, 1) == pytest.approx(5.0)
        # dani → alice é só do fechamento (3)
        assert g.get_edge_weight(3, 0) == pytest.approx(3.0)
        # charlie → alice é só comentário (2)
        assert g.get_edge_weight(2, 0) == pytest.approx(2.0)

    def test_build_all_pdf_graphs_returns_four_keys(self, data):
        graphs = GraphBuilderService().build_all_pdf_graphs(data)
        assert set(graphs.keys()) == {"comments", "issue_close", "reviews_merges", "integrated"}
        assert all(g.get_vertex_count() == 4 for g in graphs.values())

    def test_issue_close_ignores_self_closure(self, users):
        alice, *_ = users
        t = datetime.now()
        # alice fecha a própria issue → não vira aresta
        issues = [
            Issue(number=2, title="x", author=alice, created_at=t, updated_at=t,
                  url="u", state="closed", closed_by=alice, closed_at=t),
        ]
        data = CollaborationGraph(
            repository="o/r", users=users, issues=issues,
            pull_requests=[], reviews=[], comments=[], mined_at=t,
        )
        g = GraphBuilderService().build_issue_close_graph(data)
        assert g.get_edge_count() == 0
