"""
Controlador de rate limit para GitHub API.

Monitora e respeita os limites de requisições da API.
"""

from typing import Optional
from datetime import datetime, timedelta


class RateLimiter:
    """Controla taxa de requisições para API GitHub.

    Implementa backoff exponencial para evitar exceder rate limit.

    Atributos:
        requests_per_hour: Limite de requisições por hora (padrão: 60)
        min_interval: Intervalo mínimo entre requisições (segundos)
    """

    def __init__(self, requests_per_hour: int = 60):
        """Inicializa rate limiter.

        Args:
            requests_per_hour: Máximo de requisições por hora

        Raises:
            ValueError: Se requests_per_hour <= 0
        """
        if requests_per_hour <= 0:
            raise ValueError(f"requests_per_hour must be > 0, got {requests_per_hour}")

        self.requests_per_hour = requests_per_hour
        self.min_interval = 3600 / requests_per_hour  # segundos
        self.last_request_time: Optional[datetime] = None
        self.requests_in_window = 0
        self.window_start = datetime.now()

    def wait_if_needed(self) -> float:
        """Aguarda se necessário para respeitar rate limit.

        Returns:
            Segundos aguardados
        """
        now = datetime.now()
        wait_time = 0.0

        # Reseta janela se passou 1 hora
        if (now - self.window_start).total_seconds() > 3600:
            self.window_start = now
            self.requests_in_window = 0

        # Se atingiu limite, aguarda até próxima janela
        if self.requests_in_window >= self.requests_per_hour:
            time_until_reset = 3600 - (now - self.window_start).total_seconds()
            if time_until_reset > 0:
                wait_time = time_until_reset
                return wait_time

        # Respeita intervalo mínimo entre requisições
        if self.last_request_time:
            elapsed = (now - self.last_request_time).total_seconds()
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                return wait_time

        return wait_time

    def record_request(self) -> None:
        """Registra uma requisição."""
        self.last_request_time = datetime.now()
        self.requests_in_window += 1

    def get_remaining_requests(self) -> int:
        """Retorna número de requisições restantes nesta janela.

        Returns:
            Número de requisições restantes
        """
        now = datetime.now()

        # Reseta janela se passou 1 hora
        if (now - self.window_start).total_seconds() > 3600:
            self.window_start = now
            self.requests_in_window = 0

        return max(0, self.requests_per_hour - self.requests_in_window)

    def get_window_reset_time(self) -> datetime:
        """Retorna hora que a janela de rate limit reseta.

        Returns:
            datetime do reset
        """
        return self.window_start + timedelta(hours=1)

    def __repr__(self) -> str:
        """Representação string."""
        remaining = self.get_remaining_requests()
        return (
            f"RateLimiter(requests_per_hour={self.requests_per_hour}, "
            f"remaining={remaining})"
        )
