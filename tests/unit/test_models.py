"""
Testes para modelos de dados.

Testa User, Interaction, InteractionType e modelos GitHub.
"""

import pytest
from datetime import datetime

from codigos.models import (
    User,
    InteractionType,
    Interaction,
    Issue,
    PullRequest,
    Review,
    Comment,
    MetricsResult,
)


class TestUser:
    """Testes para classe User."""

    def test_create_user(self):
        """Cria um usuário válido."""
        user = User(id=123, login="alice")
        assert user.id == 123
        assert user.login == "alice"

    def test_user_is_hashable(self):
        """Usuário pode ser usado em sets/dicts."""
        user1 = User(id=1, login="alice")
        user2 = User(id=1, login="alice")
        user_set = {user1, user2}
        assert len(user_set) == 1

    def test_user_is_frozen(self):
        """Usuário é imutável após criação."""
        user = User(id=1, login="alice")
        with pytest.raises(Exception):
            user.id = 999

    def test_user_invalid_id(self):
        """Rejeita ID negativo."""
        with pytest.raises(ValueError):
            User(id=-1, login="alice")

    def test_user_invalid_login(self):
        """Rejeita login vazio."""
        with pytest.raises(ValueError):
            User(id=1, login="")


class TestInteractionType:
    """Testes para enum InteractionType."""

    def test_interaction_weights(self):
        """Tipos de interação têm pesos corretos."""
        assert InteractionType.ISSUE_COMMENT.weight == 2
        assert InteractionType.ISSUE_CLOSE.weight == 1
        assert InteractionType.PR_COMMENT.weight == 2
        assert InteractionType.PR_REVIEW.weight == 4
        assert InteractionType.PR_APPROVAL.weight == 3
        assert InteractionType.PR_MERGE.weight == 5

    def test_from_github_action_issue_comment(self):
        """Mapeia ação GitHub para tipo."""
        interaction_type = InteractionType.from_github_action("commented", "issue")
        assert interaction_type == InteractionType.ISSUE_COMMENT

    def test_from_github_action_pr_review(self):
        """Mapeia review de PR."""
        interaction_type = InteractionType.from_github_action("submitted", "pr")
        assert interaction_type == InteractionType.PR_REVIEW

    def test_from_github_action_invalid(self):
        """Rejeita ação desconhecida."""
        with pytest.raises(ValueError):
            InteractionType.from_github_action("unknown_action", "pr")


class TestInteraction:
    """Testes para classe Interaction."""

    @pytest.fixture
    def users(self):
        """Cria usuários para testes."""
        alice = User(id=1, login="alice")
        bob = User(id=2, login="bob")
        return alice, bob

    def test_create_interaction(self, users):
        """Cria uma interação válida."""
        alice, bob = users
        interaction = Interaction(
            source=alice,
            target=bob,
            interaction_type=InteractionType.PR_REVIEW,
            timestamp=datetime.now(),
            url="https://github.com/owner/repo/pull/1",
        )
        assert interaction.source == alice
        assert interaction.target == bob
        assert interaction.weight == 4

    def test_interaction_self_loop_rejected(self, users):
        """Rejeita interação self-loop."""
        alice, _ = users
        with pytest.raises(ValueError, match="self-loop"):
            Interaction(
                source=alice,
                target=alice,
                interaction_type=InteractionType.PR_REVIEW,
                timestamp=datetime.now(),
                url="https://github.com/owner/repo/pull/1",
            )

    def test_interaction_weight_property(self, users):
        """Peso da interação vem do tipo."""
        alice, bob = users
        interaction = Interaction(
            source=alice,
            target=bob,
            interaction_type=InteractionType.ISSUE_COMMENT,
            timestamp=datetime.now(),
            url="https://github.com/owner/repo/issues/1#comment",
        )
        assert interaction.weight == 2


class TestIssue:
    """Testes para classe Issue."""

    def test_create_issue(self):
        """Cria uma issue válida."""
        author = User(id=1, login="alice")
        now = datetime.now()
        issue = Issue(
            number=42,
            title="Bug fix",
            author=author,
            created_at=now,
            updated_at=now,
            url="https://github.com/owner/repo/issues/42",
        )
        assert issue.number == 42
        assert issue.state == "open"

    def test_issue_invalid_number(self):
        """Rejeita número negativo."""
        author = User(id=1, login="alice")
        now = datetime.now()
        with pytest.raises(ValueError):
            Issue(
                number=0,
                title="Bug fix",
                author=author,
                created_at=now,
                updated_at=now,
                url="https://github.com/owner/repo/issues/0",
            )


class TestPullRequest:
    """Testes para classe PullRequest."""

    def test_create_pr(self):
        """Cria um PR válido."""
        author = User(id=1, login="alice")
        now = datetime.now()
        pr = PullRequest(
            number=10,
            title="Feature",
            author=author,
            created_at=now,
            updated_at=now,
            url="https://github.com/owner/repo/pull/10",
        )
        assert pr.number == 10
        assert not pr.is_merged

    def test_pr_merged(self):
        """PR mergeado tem merged_by definido."""
        author = User(id=1, login="alice")
        merger = User(id=2, login="bob")
        now = datetime.now()
        pr = PullRequest(
            number=10,
            title="Feature",
            author=author,
            created_at=now,
            updated_at=now,
            merged_at=now,
            merged_by=merger,
            url="https://github.com/owner/repo/pull/10",
            state="merged",
        )
        assert pr.is_merged
        assert pr.merged_by == merger


class TestReview:
    """Testes para classe Review."""

    def test_create_review(self):
        """Cria um review válido."""
        author = User(id=1, login="alice")
        review = Review(
            id=1,
            author=author,
            pr_number=10,
            state="APPROVED",
            submitted_at=datetime.now(),
            url="https://github.com/owner/repo/pull/10#review-1",
        )
        assert review.is_approval

    def test_review_invalid_state(self):
        """Rejeita estado inválido."""
        author = User(id=1, login="alice")
        with pytest.raises(ValueError):
            Review(
                id=1,
                author=author,
                pr_number=10,
                state="INVALID_STATE",
                submitted_at=datetime.now(),
                url="https://github.com/owner/repo/pull/10#review-1",
            )


class TestComment:
    """Testes para classe Comment."""

    def test_create_issue_comment(self):
        """Cria comentário em issue."""
        author = User(id=1, login="alice")
        comment = Comment(
            id=1,
            author=author,
            body="Great work!",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            url="https://github.com/owner/repo/issues/1#comment-1",
            issue_number=1,
        )
        assert comment.issue_number == 1
        assert comment.pr_number is None

    def test_comment_requires_context(self):
        """Comentário precisa estar em issue ou PR."""
        author = User(id=1, login="alice")
        with pytest.raises(ValueError):
            Comment(
                id=1,
                author=author,
                body="Great work!",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                url="https://github.com/owner/repo/issues/1#comment-1",
            )


class TestMetricsResult:
    """Testes para classe MetricsResult."""

    def test_create_metrics(self):
        """Cria resultado de métricas válido."""
        user = User(id=1, login="alice")
        metrics = MetricsResult(
            user=user,
            degree_centrality=0.5,
            in_degree=5,
            out_degree=3,
            pagerank=0.15,
        )
        assert metrics.user == user
        assert metrics.degree_centrality == 0.5

    def test_metrics_invalid_centrality(self):
        """Rejeita centralidade fora de [0, 1]."""
        user = User(id=1, login="alice")
        with pytest.raises(ValueError):
            MetricsResult(user=user, degree_centrality=1.5)

    def test_metrics_invalid_pagerank(self):
        """Rejeita PageRank negativo."""
        user = User(id=1, login="alice")
        with pytest.raises(ValueError):
            MetricsResult(user=user, pagerank=-0.1)
