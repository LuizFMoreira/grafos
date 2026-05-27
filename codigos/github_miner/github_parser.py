"""
Parser para converter dados brutos da API do GitHub em modelos de domínio.

Transforma dicts JSON em objetos User, Issue, PullRequest, Review, Comment.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from ..models import (
    User,
    Issue,
    PullRequest,
    Review,
    Comment,
    InteractionType,
)
from ..exceptions.mining_exceptions import DataParsingError


class GithubParser:
    """Parser de dados da API GitHub para modelos de domínio.

    Converte JSONs brutos em objetos tipados com validação.
    """

    @staticmethod
    def parse_user(data: Dict[str, Any]) -> User:
        """Converte dict JSON para User.

        Args:
            data: Dict com 'id' e 'login'

        Returns:
            User object

        Raises:
            DataParsingError: Se dados inválidos
        """
        try:
            return User(id=int(data["id"]), login=str(data["login"]))
        except (KeyError, ValueError, TypeError) as e:
            raise DataParsingError(f"Failed to parse user: {e}")

    @staticmethod
    def parse_issue(data: Dict[str, Any]) -> Issue:
        """Converte dict JSON para Issue.

        Args:
            data: Dict com number, title, user, created_at, etc

        Returns:
            Issue object

        Raises:
            DataParsingError: Se dados inválidos
        """
        try:
            author = GithubParser.parse_user(data["user"])
            created_at = GithubParser.parse_datetime(data["created_at"])
            updated_at = GithubParser.parse_datetime(data["updated_at"])

            state = "closed" if data.get("closed_at") else "open"

            return Issue(
                number=int(data["number"]),
                title=str(data["title"]),
                author=author,
                created_at=created_at,
                updated_at=updated_at,
                url=str(data["html_url"]),
                state=state,
            )
        except (KeyError, ValueError, TypeError) as e:
            raise DataParsingError(f"Failed to parse issue: {e}")

    @staticmethod
    def parse_pull_request(data: Dict[str, Any]) -> PullRequest:
        """Converte dict JSON para PullRequest.

        Args:
            data: Dict com number, title, user, merged_by, etc

        Returns:
            PullRequest object

        Raises:
            DataParsingError: Se dados inválidos
        """
        try:
            author = GithubParser.parse_user(data["user"])
            created_at = GithubParser.parse_datetime(data["created_at"])
            updated_at = GithubParser.parse_datetime(data["updated_at"])

            merged_at = None
            merged_by = None
            state = "open"

            if data.get("merged_at"):
                merged_at = GithubParser.parse_datetime(data["merged_at"])
                merged_by_data = data.get("merged_by")
                merged_by = GithubParser.parse_user(merged_by_data) if merged_by_data else None
                state = "merged"
            elif data.get("closed_at"):
                state = "closed"

            return PullRequest(
                number=int(data["number"]),
                title=str(data["title"]),
                author=author,
                created_at=created_at,
                updated_at=updated_at,
                url=str(data["html_url"]),
                merged_at=merged_at,
                merged_by=merged_by,
                state=state,
            )
        except (KeyError, ValueError, TypeError) as e:
            raise DataParsingError(f"Failed to parse pull request: {e}")

    @staticmethod
    def parse_review(data: Dict[str, Any], pr_number: int) -> Review:
        """Converte dict JSON para Review.

        Args:
            data: Dict com id, user, state, submitted_at, etc
            pr_number: Número do PR

        Returns:
            Review object

        Raises:
            DataParsingError: Se dados inválidos
        """
        try:
            author = GithubParser.parse_user(data["user"])
            submitted_at = GithubParser.parse_datetime(data["submitted_at"])

            # Mapeia estado GitHub para nosso enum
            state_map = {
                "APPROVED": "APPROVED",
                "CHANGES_REQUESTED": "REQUESTED_CHANGES",
                "COMMENTED": "COMMENTED",
                "PENDING": "PENDING",
                "DISMISSED": "DISMISSED",
            }
            state = state_map.get(data.get("state", "PENDING"), "PENDING")

            return Review(
                id=int(data["id"]),
                author=author,
                pr_number=pr_number,
                state=state,
                submitted_at=submitted_at,
                url=str(data["html_url"]),
            )
        except (KeyError, ValueError, TypeError) as e:
            raise DataParsingError(f"Failed to parse review: {e}")

    @staticmethod
    def parse_comment(
        data: Dict[str, Any],
        issue_number: Optional[int] = None,
        pr_number: Optional[int] = None,
    ) -> Comment:
        """Converte dict JSON para Comment.

        Args:
            data: Dict com id, user, body, created_at, etc
            issue_number: Número da issue (se comentário em issue)
            pr_number: Número do PR (se comentário em PR)

        Returns:
            Comment object

        Raises:
            DataParsingError: Se dados inválidos
        """
        try:
            author = GithubParser.parse_user(data["user"])
            created_at = GithubParser.parse_datetime(data["created_at"])
            updated_at = GithubParser.parse_datetime(data["updated_at"])

            return Comment(
                id=int(data["id"]),
                author=author,
                body=str(data["body"]),
                created_at=created_at,
                updated_at=updated_at,
                url=str(data["html_url"]),
                issue_number=issue_number,
                pr_number=pr_number,
            )
        except (KeyError, ValueError, TypeError) as e:
            raise DataParsingError(f"Failed to parse comment: {e}")

    @staticmethod
    def parse_datetime(datetime_str: str) -> datetime:
        """Converte string ISO 8601 para datetime.

        Args:
            datetime_str: String no formato ISO 8601 (ex: '2023-01-15T10:30:45Z')

        Returns:
            datetime object

        Raises:
            DataParsingError: Se formato inválido
        """
        try:
            # Remove 'Z' se presente e parseia
            datetime_str = datetime_str.replace("Z", "+00:00")
            return datetime.fromisoformat(datetime_str)
        except (ValueError, TypeError) as e:
            raise DataParsingError(f"Failed to parse datetime: {e}")

    @staticmethod
    def extract_users_from_issues(issues: List[Dict[str, Any]]) -> List[User]:
        """Extrai usuários únicos de uma lista de issues.

        Args:
            issues: Lista de dicts de issues

        Returns:
            Lista de User objects únicos
        """
        users_dict = {}

        for issue in issues:
            try:
                author = GithubParser.parse_user(issue["user"])
                users_dict[author.id] = author
            except DataParsingError:
                continue

        return list(users_dict.values())

    @staticmethod
    def extract_users_from_pull_requests(
        pull_requests: List[Dict[str, Any]],
    ) -> List[User]:
        """Extrai usuários únicos de uma lista de PRs.

        Args:
            pull_requests: Lista de dicts de PRs

        Returns:
            Lista de User objects únicos
        """
        users_dict = {}

        for pr in pull_requests:
            try:
                author = GithubParser.parse_user(pr["user"])
                users_dict[author.id] = author

                if pr.get("merged_by"):
                    merger = GithubParser.parse_user(pr["merged_by"])
                    users_dict[merger.id] = merger
            except DataParsingError:
                continue

        return list(users_dict.values())

    @staticmethod
    def extract_users_from_comments(
        comments: List[Dict[str, Any]],
    ) -> List[User]:
        """Extrai usuários únicos de uma lista de comentários.

        Args:
            comments: Lista de dicts de comentários

        Returns:
            Lista de User objects únicos
        """
        users_dict = {}

        for comment in comments:
            try:
                author = GithubParser.parse_user(comment["user"])
                users_dict[author.id] = author
            except DataParsingError:
                continue

        return list(users_dict.values())

    @staticmethod
    def extract_all_unique_users(
        issues: List[Dict[str, Any]] = None,
        pull_requests: List[Dict[str, Any]] = None,
        comments: List[Dict[str, Any]] = None,
        reviews: List[Dict[str, Any]] = None,
    ) -> List[User]:
        """Extrai todos os usuários únicos de todas as fontes.

        Args:
            issues: Lista de issues (opcional)
            pull_requests: Lista de PRs (opcional)
            comments: Lista de comentários (opcional)
            reviews: Lista de reviews (opcional)

        Returns:
            Lista de User objects únicos
        """
        users_dict = {}

        for users_list in [
            GithubParser.extract_users_from_issues(issues or []),
            GithubParser.extract_users_from_pull_requests(pull_requests or []),
            GithubParser.extract_users_from_comments(comments or []),
        ]:
            for user in users_list:
                users_dict[user.id] = user

        # Extrai usuários de reviews
        for review in reviews or []:
            try:
                reviewer = GithubParser.parse_user(review["user"])
                users_dict[reviewer.id] = reviewer
            except DataParsingError:
                continue

        return list(users_dict.values())
