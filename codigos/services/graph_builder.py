"""
Construtor de grafos de colaboração a partir de dados GitHub.

Transforma CollaborationGraph em grafos ponderados de interações.
"""

from typing import Dict, Tuple
from collections import defaultdict

from ..models import (
    CollaborationGraph,
    User,
    InteractionType,
    Interaction,
)
from ..core.graph import (
    AbstractGraph,
    AdjacencyListGraph,
    AdjacencyMatrixGraph,
)
from ..exceptions.mining_exceptions import GithubMiningError


class GraphBuilderService:
    """Constrói grafos de colaboração a partir de dados GitHub.

    Transforma issues, PRs, reviews e comentários em arestas ponderadas.
    Cria 4 grafos distintos:
    1. Total: todas as interações
    2. Issues: comentários em issues
    3. Pull Requests: comentários em PRs + reviews
    4. Mentions: menções e referências

    Pesos de interação:
    - Comentário em issue: 2
    - Comentário em PR: 2
    - Review de código: 4
    - Aprovação de PR: 3
    - Merge de PR: 5
    """

    def __init__(self, use_adjacency_list: bool = True):
        """Inicializa graph builder.

        Args:
            use_adjacency_list: Se True usa AdjacencyListGraph,
                               senão usa AdjacencyMatrixGraph
        """
        self.use_adjacency_list = use_adjacency_list

    def _create_graph(self, vertex_count: int) -> AbstractGraph:
        """Cria grafo vazio (lista ou matriz).

        Args:
            vertex_count: Número de vértices

        Returns:
            Graph vazio (AdjacencyListGraph ou AdjacencyMatrixGraph)
        """
        if self.use_adjacency_list:
            return AdjacencyListGraph(vertex_count)
        else:
            return AdjacencyMatrixGraph(vertex_count)

    def build_collaboration_graph(
        self, collaboration_data: CollaborationGraph
    ) -> AbstractGraph:
        """Constrói grafo completo de colaboração.

        Inclui todas as interações:
        - Comentários em issues
        - Comentários em PRs
        - Reviews de código
        - Merges de PRs

        Args:
            collaboration_data: CollaborationGraph minerado

        Returns:
            AbstractGraph com todas as interações

        Raises:
            GithubMiningError: Se dados inválidos
        """
        if not collaboration_data.users:
            raise GithubMiningError("No users found in collaboration data")

        user_index = {user.id: idx for idx, user in enumerate(collaboration_data.users)}
        vertex_count = len(collaboration_data.users)
        graph = self._create_graph(vertex_count)

        # Adiciona rótulos de usuários
        for user in collaboration_data.users:
            idx = user_index[user.id]
            graph.set_vertex_label(idx, user.login)

        # Processa comentários em issues
        for comment in collaboration_data.comments:
            if comment.issue_number and comment.author and not hasattr(comment.author, '__iter__'):
                author_idx = user_index.get(comment.author.id)
                if author_idx is not None:
                    # Encontra autor da issue
                    for issue in collaboration_data.issues:
                        if issue.number == comment.issue_number:
                            if issue.author:
                                target_idx = user_index.get(issue.author.id)
                                if target_idx is not None and author_idx != target_idx:
                                    graph.add_edge(author_idx, target_idx, weight=2.0)
                            break

        # Processa comentários em PRs
        for comment in collaboration_data.comments:
            if comment.pr_number and comment.author:
                author_idx = user_index.get(comment.author.id)
                if author_idx is not None:
                    # Encontra autor do PR
                    for pr in collaboration_data.pull_requests:
                        if pr.number == comment.pr_number:
                            if pr.author:
                                target_idx = user_index.get(pr.author.id)
                                if target_idx is not None and author_idx != target_idx:
                                    graph.add_edge(author_idx, target_idx, weight=2.0)
                            break

        # Processa reviews
        for review in collaboration_data.reviews:
            if review.author:
                reviewer_idx = user_index.get(review.author.id)
                if reviewer_idx is not None:
                    # Encontra autor do PR
                    for pr in collaboration_data.pull_requests:
                        if pr.number == review.pr_number:
                            if pr.author:
                                author_idx = user_index.get(pr.author.id)
                                if author_idx is not None and reviewer_idx != author_idx:
                                    weight = 4.0 if review.state == "APPROVED" else 4.0
                                    graph.add_edge(reviewer_idx, author_idx, weight=weight)
                            break

        # Processa merges de PRs
        for pr in collaboration_data.pull_requests:
            if pr.merged_by and pr.author:
                merger_idx = user_index.get(pr.merged_by.id)
                author_idx = user_index.get(pr.author.id)
                if (
                    merger_idx is not None
                    and author_idx is not None
                    and merger_idx != author_idx
                ):
                    graph.add_edge(merger_idx, author_idx, weight=5.0)

        return graph

    def build_issues_graph(
        self, collaboration_data: CollaborationGraph
    ) -> AbstractGraph:
        """Constrói grafo de interações em issues.

        Apenas comentários em issues.

        Args:
            collaboration_data: CollaborationGraph minerado

        Returns:
            AbstractGraph com interações em issues
        """
        if not collaboration_data.users:
            raise GithubMiningError("No users found in collaboration data")

        user_index = {user.id: idx for idx, user in enumerate(collaboration_data.users)}
        vertex_count = len(collaboration_data.users)
        graph = self._create_graph(vertex_count)

        # Adiciona rótulos
        for user in collaboration_data.users:
            idx = user_index[user.id]
            graph.set_vertex_label(idx, user.login)

        # Apenas comentários em issues
        for comment in collaboration_data.comments:
            if comment.issue_number and comment.author:
                author_idx = user_index.get(comment.author.id)
                if author_idx is not None:
                    for issue in collaboration_data.issues:
                        if issue.number == comment.issue_number:
                            if issue.author:
                                target_idx = user_index.get(issue.author.id)
                                if target_idx is not None and author_idx != target_idx:
                                    graph.add_edge(author_idx, target_idx, weight=2.0)
                            break

        return graph

    def build_pull_requests_graph(
        self, collaboration_data: CollaborationGraph
    ) -> AbstractGraph:
        """Constrói grafo de interações em PRs.

        Comentários em PRs, reviews e merges.

        Args:
            collaboration_data: CollaborationGraph minerado

        Returns:
            AbstractGraph com interações em PRs
        """
        if not collaboration_data.users:
            raise GithubMiningError("No users found in collaboration data")

        user_index = {user.id: idx for idx, user in enumerate(collaboration_data.users)}
        vertex_count = len(collaboration_data.users)
        graph = self._create_graph(vertex_count)

        # Adiciona rótulos
        for user in collaboration_data.users:
            idx = user_index[user.id]
            graph.set_vertex_label(idx, user.login)

        # Comentários em PRs
        for comment in collaboration_data.comments:
            if comment.pr_number and comment.author:
                author_idx = user_index.get(comment.author.id)
                if author_idx is not None:
                    for pr in collaboration_data.pull_requests:
                        if pr.number == comment.pr_number:
                            if pr.author:
                                target_idx = user_index.get(pr.author.id)
                                if target_idx is not None and author_idx != target_idx:
                                    graph.add_edge(author_idx, target_idx, weight=2.0)
                            break

        # Reviews
        for review in collaboration_data.reviews:
            if review.author:
                reviewer_idx = user_index.get(review.author.id)
                if reviewer_idx is not None:
                    for pr in collaboration_data.pull_requests:
                        if pr.number == review.pr_number:
                            if pr.author:
                                author_idx = user_index.get(pr.author.id)
                                if author_idx is not None and reviewer_idx != author_idx:
                                    graph.add_edge(reviewer_idx, author_idx, weight=4.0)
                            break

        # Merges
        for pr in collaboration_data.pull_requests:
            if pr.merged_by and pr.author:
                merger_idx = user_index.get(pr.merged_by.id)
                author_idx = user_index.get(pr.author.id)
                if (
                    merger_idx is not None
                    and author_idx is not None
                    and merger_idx != author_idx
                ):
                    graph.add_edge(merger_idx, author_idx, weight=5.0)

        return graph

    def build_all_graphs(
        self, collaboration_data: CollaborationGraph
    ) -> Dict[str, AbstractGraph]:
        """Constrói todos os 4 grafos de uma vez.

        Args:
            collaboration_data: CollaborationGraph minerado

        Returns:
            Dict com chaves: 'total', 'issues', 'pull_requests'
        """
        return {
            "total": self.build_collaboration_graph(collaboration_data),
            "issues": self.build_issues_graph(collaboration_data),
            "pull_requests": self.build_pull_requests_graph(collaboration_data),
        }

    @staticmethod
    def get_graph_statistics(graph: AbstractGraph) -> Dict[str, int]:
        """Retorna estatísticas do grafo.

        Args:
            graph: Grafo a analisar

        Returns:
            Dict com 'vertices', 'edges', 'density'
        """
        v_count = graph.get_vertex_count()
        e_count = graph.get_edge_count()
        max_edges = v_count * (v_count - 1)  # Grafo direcionado simples
        density = e_count / max_edges if max_edges > 0 else 0.0

        return {
            "vertices": v_count,
            "edges": e_count,
            "max_edges": max_edges,
            "density": density,
            "is_connected": graph.is_connected(),
            "is_complete": graph.is_complete_graph(),
        }
