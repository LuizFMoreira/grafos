"""
Cliente HTTP para a API REST do GitHub.

Responsável por fazer requisições autenticadas, tratar rate limit,
e retornar dados brutos (dicts) da API.
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import requests

from ..exceptions.mining_exceptions import (
    GithubMiningError,
    RateLimitExceededError,
    InvalidRepositoryError,
    DataParsingError,
)


class GithubClient:
    """Cliente para comunicação com API REST do GitHub.

    Gerencia autenticação, rate limiting, paginação e tratamento de erros.

    Atributos:
        base_url: URL base da API (https://api.github.com)
        token: Token de autenticação pessoal do GitHub
        per_page: Registros por página (default: 100)
        max_retries: Número máximo de tentativas com rate limit
        retry_wait: Segundos de espera entre tentativas (default: 60)
    """

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: str,
        per_page: int = 100,
        max_retries: int = 3,
        retry_wait: int = 60,
    ):
        """Inicializa cliente GitHub.

        Args:
            token: Token de autenticação do GitHub
            per_page: Registros por página (max: 100)
            max_retries: Tentativas com rate limit
            retry_wait: Segundos de espera entre tentativas

        Raises:
            ValueError: Se token vazio ou per_page inválido
        """
        if not token or not isinstance(token, str):
            raise ValueError(f"Invalid token: {token}")
        if per_page < 1 or per_page > 100:
            raise ValueError(f"per_page must be 1-100, got {per_page}")

        self.token = token
        self.per_page = per_page
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "GithubAnalyzer/1.0",
            }
        )

    def _check_rate_limit(self) -> None:
        """Verifica rate limit e aguarda se necessário.

        Raises:
            RateLimitExceededError: Se rate limit esgotado após max_retries
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/rate_limit")
            response.raise_for_status()
            data = response.json()

            remaining = data["resources"]["core"]["remaining"]
            reset_time = data["resources"]["core"]["reset"]

            if remaining < 10:
                reset_datetime = datetime.fromtimestamp(reset_time)
                wait_seconds = (reset_datetime - datetime.now()).total_seconds()

                if wait_seconds > 0:
                    raise RateLimitExceededError(
                        f"Rate limit near zero. Resets in {wait_seconds:.0f}s"
                    )
        except requests.RequestException as e:
            raise GithubMiningError(f"Failed to check rate limit: {e}")

    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Faz requisição HTTP com tratamento de rate limit.

        Args:
            method: Método HTTP ('GET', 'POST', etc)
            endpoint: Endpoint da API (ex: '/repos/owner/repo/issues')
            **kwargs: Argumentos adicionais para requests

        Returns:
            Response JSON como dict

        Raises:
            GithubMiningError: Erro na requisição
            RateLimitExceededError: Rate limit excedido
        """
        url = f"{self.BASE_URL}{endpoint}"
        retries = 0

        while retries < self.max_retries:
            try:
                self._check_rate_limit()

                response = self.session.request(method, url, **kwargs)

                if response.status_code == 403:
                    raise RateLimitExceededError("Rate limit exceeded")
                if response.status_code == 404:
                    raise InvalidRepositoryError(
                        f"Repository not found: {endpoint}"
                    )
                if response.status_code >= 400:
                    raise GithubMiningError(
                        f"HTTP {response.status_code}: {response.text}"
                    )

                return response.json()

            except RateLimitExceededError:
                retries += 1
                if retries >= self.max_retries:
                    raise
                time.sleep(self.retry_wait)

            except requests.RequestException as e:
                raise GithubMiningError(f"Request failed: {e}")

        raise GithubMiningError("Max retries exceeded")

    def _paginate(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Busca todos os registros com paginação automática.

        Args:
            endpoint: Endpoint da API
            params: Parâmetros de query

        Returns:
            Lista com todos os registros
        """
        if params is None:
            params = {}

        params["per_page"] = self.per_page
        all_data = []
        page = 1

        while True:
            params["page"] = page
            data = self._make_request("GET", endpoint, params=params)

            if not isinstance(data, list):
                return [data]

            if len(data) == 0:
                break

            all_data.extend(data)
            page += 1

        return all_data

    def get_issues(
        self, owner: str, repo: str, state: str = "all"
    ) -> List[Dict[str, Any]]:
        """Busca todas as issues do repositório.

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            state: 'open', 'closed' ou 'all'

        Returns:
            Lista de issues (dicts)

        Raises:
            InvalidRepositoryError: Repositório não existe
        """
        if not owner or not repo:
            raise ValueError("owner and repo must be non-empty strings")

        endpoint = f"/repos/{owner}/{repo}/issues"
        return self._paginate(endpoint, {"state": state})

    def get_pull_requests(
        self, owner: str, repo: str, state: str = "all"
    ) -> List[Dict[str, Any]]:
        """Busca todos os pull requests do repositório.

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            state: 'open', 'closed' ou 'all'

        Returns:
            Lista de PRs (dicts)

        Raises:
            InvalidRepositoryError: Repositório não existe
        """
        if not owner or not repo:
            raise ValueError("owner and repo must be non-empty strings")

        endpoint = f"/repos/{owner}/{repo}/pulls"
        return self._paginate(endpoint, {"state": state})

    def get_issue_comments(
        self, owner: str, repo: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Busca comentários de uma issue.

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            issue_number: Número da issue

        Returns:
            Lista de comentários (dicts)
        """
        if issue_number < 1:
            raise ValueError(f"issue_number must be >= 1, got {issue_number}")

        endpoint = f"/repos/{owner}/{repo}/issues/{issue_number}/comments"
        return self._paginate(endpoint)

    def get_pull_request_comments(
        self, owner: str, repo: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Busca comentários de review de um PR.

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            pr_number: Número do PR

        Returns:
            Lista de comentários (dicts)
        """
        if pr_number < 1:
            raise ValueError(f"pr_number must be >= 1, got {pr_number}")

        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        return self._paginate(endpoint)

    def get_pull_request_reviews(
        self, owner: str, repo: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Busca reviews de um PR.

        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            pr_number: Número do PR

        Returns:
            Lista de reviews (dicts)
        """
        if pr_number < 1:
            raise ValueError(f"pr_number must be >= 1, got {pr_number}")

        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        return self._paginate(endpoint)

    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Busca informações do repositório.

        Args:
            owner: Dono do repositório
            repo: Nome do repositório

        Returns:
            Informações do repositório (dict)

        Raises:
            InvalidRepositoryError: Repositório não existe
        """
        if not owner or not repo:
            raise ValueError("owner and repo must be non-empty strings")

        endpoint = f"/repos/{owner}/{repo}"
        return self._make_request("GET", endpoint)

    def close(self) -> None:
        """Fecha a sessão HTTP."""
        self.session.close()

    def __enter__(self):
        """Context manager: entrada."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: saída."""
        self.close()
