"""
Transformador de dados da API GitHub.

Orquestra a coleta e transformação de dados brutos em modelos de domínio.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from .github_client import GithubClient
from .github_parser import GithubParser
from ..models import (
    User,
    Issue,
    PullRequest,
    Review,
    Comment,
    CollaborationGraph,
)
from ..exceptions.mining_exceptions import GithubMiningError


class DataTransformer:
    """Orquestra coleta e transformação de dados do GitHub.

    Combina GithubClient (requisições HTTP) com GithubParser
    (transformação para modelos) para minerar repositório completo.
    """

    def __init__(self, client: GithubClient):
        """Inicializa transformador.

        Args:
            client: Instância de GithubClient configurado
        """
        if not isinstance(client, GithubClient):
            raise TypeError(f"Expected GithubClient, got {type(client)}")

        self.client = client

    def mine_repository(
        self,
        owner: str,
        repo: str,
        include_comments: bool = True,
        include_reviews: bool = True,
    ) -> CollaborationGraph:
        """Minera um repositório completo e retorna grafo de colaboração.

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            include_comments: Se deve minerar comentários
            include_reviews: Se deve minerar reviews

        Returns:
            CollaborationGraph com todos os dados minerados

        Raises:
            GithubMiningError: Erro durante mineração
        """
        try:
            # 1. Busca dados brutos
            raw_issues = self.client.get_issues(owner, repo)
            raw_pull_requests = self.client.get_pull_requests(owner, repo)

            raw_reviews = []
            raw_comments = []

            if include_reviews:
                raw_reviews = self._get_all_reviews(owner, repo, raw_pull_requests)

            if include_comments:
                raw_comments = self._get_all_comments(owner, repo)

            # 2. Parseia dados — pula registros com autor deletado (user=null)
            issues = []
            for raw in raw_issues:
                try:
                    issues.append(GithubParser.parse_issue(raw))
                except Exception:
                    continue
            pull_requests = []
            for raw in raw_pull_requests:
                try:
                    pull_requests.append(GithubParser.parse_pull_request(raw))
                except Exception:
                    continue
            reviews = []
            for raw in raw_reviews:
                try:
                    reviews.append(
                        GithubParser.parse_review(raw, raw["pull_request"]["number"])
                    )
                except Exception:
                    continue
            comments = self._parse_comments(raw_comments)

            # 3. Extrai usuários únicos
            users = GithubParser.extract_all_unique_users(
                issues=[raw for raw in raw_issues],
                pull_requests=[raw for raw in raw_pull_requests],
                comments=[raw for raw in raw_comments],
                reviews=[raw for raw in raw_reviews],
            )

            # 4. Cria grafo de colaboração
            graph = CollaborationGraph(
                repository=f"{owner}/{repo}",
                users=users,
                issues=issues,
                pull_requests=pull_requests,
                reviews=reviews,
                comments=comments,
                mined_at=datetime.now(),
            )

            return graph

        except Exception as e:
            raise GithubMiningError(f"Failed to mine repository: {e}")

    def _get_all_reviews(
        self, owner: str, repo: str, pull_requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Busca reviews de todos os PRs (ainda requer N chamadas — sem endpoint bulk na API REST).

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            pull_requests: Lista de dicts de PRs

        Returns:
            Lista de reviews (dicts)
        """
        all_reviews = []
        total = len(pull_requests)

        for i, pr in enumerate(pull_requests, 1):
            if i % 50 == 0 or i == total:
                print(f"    reviews: {i}/{total} PRs processados...")
            try:
                pr_number = pr["number"]
                reviews = self.client.get_pull_request_reviews(owner, repo, pr_number)
                for review in reviews:
                    review["pull_request"] = {"number": pr_number}
                all_reviews.extend(reviews)
            except Exception:
                continue

        return all_reviews

    def _get_all_comments(
        self,
        owner: str,
        repo: str,
    ) -> List[Dict[str, Any]]:
        """Busca comentários de issues e PRs usando endpoints bulk (2 chamadas paginadas).

        Usa GET /issues/comments e GET /pulls/comments em vez de iterar por item,
        eliminando o problema N+1.

        Returns:
            Lista de comentários (dicts) com _issue_number e _pr_number inferidos
        """
        import re
        all_comments = []

        issue_comments = self.client.get_all_issue_comments(owner, repo)
        for comment in issue_comments:
            issue_url = comment.get("issue_url", "")
            match = re.search(r"/issues/(\d+)$", issue_url)
            comment["_issue_number"] = int(match.group(1)) if match else None
            comment["_pr_number"] = None
            all_comments.append(comment)

        pr_comments = self.client.get_all_pull_request_comments(owner, repo)
        for comment in pr_comments:
            pr_url = comment.get("pull_request_url", "")
            match = re.search(r"/pulls/(\d+)$", pr_url)
            comment["_issue_number"] = None
            comment["_pr_number"] = int(match.group(1)) if match else None
            all_comments.append(comment)

        return all_comments

    def _parse_comments(self, raw_comments: List[Dict[str, Any]]) -> List[Comment]:
        """Parseia lista de comentários com contexto.

        Args:
            raw_comments: Lista de dicts de comentários (com _issue_number e _pr_number)

        Returns:
            Lista de Comment objects
        """
        comments = []

        for raw in raw_comments:
            try:
                comment = GithubParser.parse_comment(
                    raw,
                    issue_number=raw.get("_issue_number"),
                    pr_number=raw.get("_pr_number"),
                )
                comments.append(comment)
            except Exception:
                continue

        return comments
