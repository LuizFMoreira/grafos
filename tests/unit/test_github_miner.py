"""
Testes para GitHub miner (client, parser, transformer).

Testes unitários sem fazer requisições reais à API.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from codigos.github_miner import (
    GithubClient,
    GithubParser,
    RateLimiter,
    DataTransformer,
)
from codigos.models import User, InteractionType
from codigos.exceptions.mining_exceptions import (
    GithubMiningError,
    RateLimitExceededError,
    InvalidRepositoryError,
    DataParsingError,
)


class TestGithubClient:
    """Testes para GithubClient."""

    def test_init_valid_token(self):
        """Cria cliente com token válido."""
        client = GithubClient(token="test_token_123")
        assert client.token == "test_token_123"
        assert client.per_page == 100

    def test_init_invalid_token(self):
        """Rejeita token vazio."""
        with pytest.raises(ValueError):
            GithubClient(token="")

    def test_init_invalid_per_page(self):
        """Rejeita per_page fora do intervalo."""
        with pytest.raises(ValueError):
            GithubClient(token="token", per_page=101)
        with pytest.raises(ValueError):
            GithubClient(token="token", per_page=0)

    def test_context_manager(self):
        """Cliente funciona como context manager."""
        with GithubClient(token="test_token") as client:
            assert client.token == "test_token"

    @patch("codigos.github_miner.github_client.requests.Session.request")
    def test_get_issues(self, mock_request):
        """Busca issues do repositório."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "Bug",
                "user": {"id": 1, "login": "alice"},
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/1",
                "closed_at": None,
            }
        ]
        mock_request.return_value = mock_response

        client = GithubClient(token="test_token")
        issues = client.get_issues("owner", "repo")

        assert len(issues) > 0
        assert issues[0]["number"] == 1

    def test_get_issues_invalid_params(self):
        """Rejeita parâmetros inválidos."""
        client = GithubClient(token="test_token")
        with pytest.raises(ValueError):
            client.get_issues("", "repo")


class TestGithubParser:
    """Testes para GithubParser."""

    def test_parse_user_valid(self):
        """Parseia usuário válido."""
        data = {"id": 123, "login": "alice"}
        user = GithubParser.parse_user(data)
        assert user.id == 123
        assert user.login == "alice"

    def test_parse_user_invalid_missing_id(self):
        """Rejeita usuário sem id."""
        data = {"login": "alice"}
        with pytest.raises(DataParsingError):
            GithubParser.parse_user(data)

    def test_parse_issue_valid(self):
        """Parseia issue válida."""
        data = {
            "number": 42,
            "title": "Bug fix",
            "user": {"id": 1, "login": "alice"},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "html_url": "https://github.com/owner/repo/issues/42",
            "closed_at": None,
        }
        issue = GithubParser.parse_issue(data)
        assert issue.number == 42
        assert issue.state == "open"

    def test_parse_issue_closed(self):
        """Parseia issue fechada."""
        data = {
            "number": 42,
            "title": "Bug fix",
            "user": {"id": 1, "login": "alice"},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "html_url": "https://github.com/owner/repo/issues/42",
            "closed_at": "2023-01-02T00:00:00Z",
        }
        issue = GithubParser.parse_issue(data)
        assert issue.state == "closed"

    def test_parse_pull_request_not_merged(self):
        """Parseia PR não mergeado."""
        data = {
            "number": 10,
            "title": "Feature",
            "user": {"id": 1, "login": "alice"},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "html_url": "https://github.com/owner/repo/pull/10",
            "merged_at": None,
            "merged_by": None,
            "closed_at": None,
        }
        pr = GithubParser.parse_pull_request(data)
        assert not pr.is_merged
        assert pr.state == "open"

    def test_parse_pull_request_merged(self):
        """Parseia PR mergeado."""
        data = {
            "number": 10,
            "title": "Feature",
            "user": {"id": 1, "login": "alice"},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "html_url": "https://github.com/owner/repo/pull/10",
            "merged_at": "2023-01-02T00:00:00Z",
            "merged_by": {"id": 2, "login": "bob"},
            "closed_at": None,
        }
        pr = GithubParser.parse_pull_request(data)
        assert pr.is_merged
        assert pr.state == "merged"
        assert pr.merged_by.login == "bob"

    def test_parse_review_approved(self):
        """Parseia review de aprovação."""
        data = {
            "id": 1,
            "user": {"id": 1, "login": "alice"},
            "state": "APPROVED",
            "submitted_at": "2023-01-01T00:00:00Z",
            "html_url": "https://github.com/owner/repo/pull/10#review-1",
        }
        review = GithubParser.parse_review(data, pr_number=10)
        assert review.is_approval
        assert review.state == "APPROVED"

    def test_parse_datetime_valid(self):
        """Parseia datetime ISO 8601."""
        dt = GithubParser.parse_datetime("2023-01-15T10:30:45Z")
        assert isinstance(dt, datetime)
        assert dt.year == 2023
        assert dt.month == 1
        assert dt.day == 15

    def test_parse_datetime_invalid(self):
        """Rejeita datetime inválido."""
        with pytest.raises(DataParsingError):
            GithubParser.parse_datetime("invalid-date")

    def test_extract_users_from_issues(self):
        """Extrai usuários únicos de issues."""
        issues = [
            {
                "number": 1,
                "title": "Issue 1",
                "user": {"id": 1, "login": "alice"},
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/1",
                "closed_at": None,
            },
            {
                "number": 2,
                "title": "Issue 2",
                "user": {"id": 1, "login": "alice"},  # Mesmo usuário
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/2",
                "closed_at": None,
            },
        ]
        users = GithubParser.extract_users_from_issues(issues)
        assert len(users) == 1
        assert users[0].login == "alice"


class TestRateLimiter:
    """Testes para RateLimiter."""

    def test_init_valid(self):
        """Cria rate limiter válido."""
        limiter = RateLimiter(requests_per_hour=60)
        assert limiter.requests_per_hour == 60

    def test_init_invalid(self):
        """Rejeita requests_per_hour <= 0."""
        with pytest.raises(ValueError):
            RateLimiter(requests_per_hour=0)

    def test_record_request(self):
        """Registra requisição."""
        limiter = RateLimiter(requests_per_hour=10)
        limiter.record_request()
        assert limiter.requests_in_window == 1

    def test_get_remaining_requests(self):
        """Calcula requisições restantes."""
        limiter = RateLimiter(requests_per_hour=10)
        remaining = limiter.get_remaining_requests()
        assert remaining == 10

        limiter.record_request()
        remaining = limiter.get_remaining_requests()
        assert remaining == 9

    def test_wait_if_needed_no_wait(self):
        """Não aguarda se há limite disponível."""
        limiter = RateLimiter(requests_per_hour=1000)
        wait_time = limiter.wait_if_needed()
        assert wait_time == 0.0


class TestDataTransformer:
    """Testes para DataTransformer."""

    def test_init_valid_client(self):
        """Cria transformer com cliente válido."""
        client = GithubClient(token="test_token")
        transformer = DataTransformer(client)
        assert transformer.client == client

    def test_init_invalid_client(self):
        """Rejeita cliente inválido."""
        with pytest.raises(TypeError):
            DataTransformer(client="invalid")

    @patch.object(GithubClient, "get_issues")
    @patch.object(GithubClient, "get_pull_requests")
    @patch.object(GithubClient, "get_pull_request_reviews")
    @patch.object(GithubClient, "get_issue_comments")
    @patch.object(GithubClient, "get_pull_request_comments")
    def test_mine_repository_minimal(
        self, mock_pr_comments, mock_issue_comments, mock_reviews, mock_prs, mock_issues
    ):
        """Minera repositório com dados mínimos."""
        mock_issues.return_value = []
        mock_prs.return_value = []
        mock_reviews.return_value = []
        mock_issue_comments.return_value = []
        mock_pr_comments.return_value = []

        client = GithubClient(token="test_token")
        transformer = DataTransformer(client)

        graph = transformer.mine_repository("owner", "repo")

        assert graph.repository == "owner/repo"
        assert graph.user_count == 0
        assert graph.interaction_count == 0
