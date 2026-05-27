"""
Tipos de interação entre usuários no GitHub.

Define os diferentes tipos de colaboração e seus respectivos pesos.
"""

from enum import Enum


class InteractionType(Enum):
    """Tipos de interação com pesos definidos.

    Pesos refletem a "força" da colaboração:
    - Comentário: interação leve (peso 2)
    - Review: análise de código (peso 4)
    - Merge: aprovação final (peso 5)
    - Close: resolução de issue (peso 1)
    - Approval: aprovação de PR (peso 3)

    Exemplo:
        >>> InteractionType.PR_REVIEW.value
        4
        >>> InteractionType.ISSUE_COMMENT.name
        'ISSUE_COMMENT'
    """

    ISSUE_COMMENT = 2  # Comentário em issue
    ISSUE_CLOSE = 1    # Fechamento de issue
    PR_COMMENT = 2     # Comentário em PR
    PR_REVIEW = 4      # Review de código
    PR_APPROVAL = 3    # Aprovação de PR
    PR_MERGE = 5       # Merge de PR

    @property
    def weight(self) -> int:
        """Retorna o peso da interação."""
        return self.value

    @classmethod
    def from_github_action(cls, action: str, context: str = "pr") -> "InteractionType":
        """Mapeia ação do GitHub para tipo de interação.

        Args:
            action: Ação do GitHub ('commented', 'reviewed', 'approved', etc)
            context: Contexto ('issue' ou 'pr')

        Returns:
            InteractionType correspondente

        Raises:
            ValueError: Se ação não é mapeável
        """
        mapping = {
            ("commented", "issue"): cls.ISSUE_COMMENT,
            ("commented", "pr"): cls.PR_COMMENT,
            ("closed", "issue"): cls.ISSUE_CLOSE,
            ("submitted", "pr"): cls.PR_REVIEW,
            ("approved", "pr"): cls.PR_APPROVAL,
            ("merged", "pr"): cls.PR_MERGE,
        }

        key = (action.lower(), context.lower())
        if key not in mapping:
            raise ValueError(f"Unknown action: {action} in context: {context}")

        return mapping[key]
