"""Construção dos grafos de colaboração a partir de dados GitHub.

Implementa a modelagem exigida pelo enunciado (TP-ES): três grafos separados
por tipo de relação + um grafo integrado ponderado.

Pesos do grafo integrado (definidos pelo enunciado):
    - Comentário em issue ou PR ........... 2
    - Fechamento de issue por outro usuário 3
    - Revisão / aprovação de PR ........... 4
    - Merge de PR ......................... 5
"""

from typing import Dict

from ..models import CollaborationGraph
from ..core.graph import AbstractGraph, AdjacencyListGraph, AdjacencyMatrixGraph
from ..exceptions.mining_exceptions import GithubMiningError


# Pesos definidos pelo PDF (Etapa 1). Centralizados para que a
# refatoração e o relatório usem o mesmo lugar.
WEIGHT_COMMENT = 2.0
WEIGHT_ISSUE_CLOSE = 3.0
WEIGHT_REVIEW = 4.0
WEIGHT_MERGE = 5.0


class GraphBuilderService:
    """Constrói os grafos de colaboração exigidos pelo TP.

    Quatro grafos:
        - Grafo 1 (build_comments_graph): comentários em issues ou PRs.
        - Grafo 2 (build_issue_close_graph): fechamento de issue por terceiro.
        - Grafo 3 (build_reviews_merges_graph): reviews/aprovações + merges.
        - Grafo integrado (build_integrated_graph): combinação ponderada das três.

    Mantém também `build_collaboration_graph`, `build_issues_graph`,
    `build_pull_requests_graph` e `build_all_graphs` como aliases para
    compatibilidade com a CLI e testes anteriores.
    """

    def __init__(self, use_adjacency_list: bool = True):
        self.use_adjacency_list = use_adjacency_list

    # ---------- infraestrutura ----------

    def _create_graph(self, vertex_count: int) -> AbstractGraph:
        if self.use_adjacency_list:
            return AdjacencyListGraph(vertex_count)
        return AdjacencyMatrixGraph(vertex_count)

    def _new_labelled_graph(self, data: CollaborationGraph):
        if not data.users:
            raise GithubMiningError("No users found in collaboration data")

        user_index = {u.id: idx for idx, u in enumerate(data.users)}
        graph = self._create_graph(len(data.users))
        for user in data.users:
            graph.set_vertex_label(user_index[user.id], user.login)
        return graph, user_index

    @staticmethod
    def _safe_add(graph, src_idx, dst_idx, weight):
        if src_idx is None or dst_idx is None or src_idx == dst_idx:
            return
        graph.add_edge(src_idx, dst_idx, weight=weight)

    # ---------- iteradores de interações (uma única travessia O(N)) ----------

    @staticmethod
    def _iter_comment_edges(data: CollaborationGraph):
        """Gera (autor_comentario, autor_da_issue_ou_pr) por comentário.

        Comentário em issue/PR: a aresta vai do comentarista para o autor
        do artefato comentado.
        """
        issue_author = {i.number: i.author for i in data.issues if i.author}
        pr_author = {p.number: p.author for p in data.pull_requests if p.author}
        for c in data.comments:
            if not c.author:
                continue
            if c.issue_number and c.issue_number in issue_author:
                yield c.author, issue_author[c.issue_number]
            elif c.pr_number and c.pr_number in pr_author:
                yield c.author, pr_author[c.pr_number]

    @staticmethod
    def _iter_issue_close_edges(data: CollaborationGraph):
        """Gera (quem_fechou, autor_da_issue) — apenas se diferentes."""
        for issue in data.issues:
            if issue.state == "closed" and issue.closed_by and issue.author:
                if issue.closed_by.id != issue.author.id:
                    yield issue.closed_by, issue.author

    @staticmethod
    def _iter_review_edges(data: CollaborationGraph):
        """Gera (reviewer, autor_pr) por review submetido."""
        pr_author = {p.number: p.author for p in data.pull_requests if p.author}
        for review in data.reviews:
            if review.author and review.pr_number in pr_author:
                yield review.author, pr_author[review.pr_number]

    @staticmethod
    def _iter_merge_edges(data: CollaborationGraph):
        """Gera (quem_fez_merge, autor_pr)."""
        for pr in data.pull_requests:
            if pr.merged_by and pr.author:
                yield pr.merged_by, pr.author

    # ---------- API exigida pelo enunciado ----------

    def build_comments_graph(self, data: CollaborationGraph) -> AbstractGraph:
        """Grafo 1: comentários em issues ou pull requests."""
        graph, idx = self._new_labelled_graph(data)
        for src, dst in self._iter_comment_edges(data):
            self._safe_add(graph, idx.get(src.id), idx.get(dst.id), WEIGHT_COMMENT)
        return graph

    def build_issue_close_graph(self, data: CollaborationGraph) -> AbstractGraph:
        """Grafo 2: fechamento de issue por outro usuário."""
        graph, idx = self._new_labelled_graph(data)
        for closer, author in self._iter_issue_close_edges(data):
            self._safe_add(graph, idx.get(closer.id), idx.get(author.id), WEIGHT_ISSUE_CLOSE)
        return graph

    def build_reviews_merges_graph(self, data: CollaborationGraph) -> AbstractGraph:
        """Grafo 3: reviews/aprovações e merges de PRs."""
        graph, idx = self._new_labelled_graph(data)
        for reviewer, author in self._iter_review_edges(data):
            self._safe_add(graph, idx.get(reviewer.id), idx.get(author.id), WEIGHT_REVIEW)
        for merger, author in self._iter_merge_edges(data):
            self._safe_add(graph, idx.get(merger.id), idx.get(author.id), WEIGHT_MERGE)
        return graph

    def build_integrated_graph(self, data: CollaborationGraph) -> AbstractGraph:
        """Grafo integrado: combina todas as interações com pesos do PDF."""
        graph, idx = self._new_labelled_graph(data)
        for src, dst in self._iter_comment_edges(data):
            self._safe_add(graph, idx.get(src.id), idx.get(dst.id), WEIGHT_COMMENT)
        for closer, author in self._iter_issue_close_edges(data):
            self._safe_add(graph, idx.get(closer.id), idx.get(author.id), WEIGHT_ISSUE_CLOSE)
        for reviewer, author in self._iter_review_edges(data):
            self._safe_add(graph, idx.get(reviewer.id), idx.get(author.id), WEIGHT_REVIEW)
        for merger, author in self._iter_merge_edges(data):
            self._safe_add(graph, idx.get(merger.id), idx.get(author.id), WEIGHT_MERGE)
        return graph

    def build_all_pdf_graphs(self, data: CollaborationGraph) -> Dict[str, AbstractGraph]:
        """Devolve exatamente os 3+1 grafos exigidos pelo enunciado."""
        return {
            "comments": self.build_comments_graph(data),
            "issue_close": self.build_issue_close_graph(data),
            "reviews_merges": self.build_reviews_merges_graph(data),
            "integrated": self.build_integrated_graph(data),
        }

    # ---------- aliases de compatibilidade ----------

    def build_collaboration_graph(self, data: CollaborationGraph) -> AbstractGraph:
        """Alias para o grafo integrado (compatibilidade com CLI/testes)."""
        return self.build_integrated_graph(data)

    def build_issues_graph(self, data: CollaborationGraph) -> AbstractGraph:
        """Alias de compatibilidade: grafo só com comentários em issues."""
        graph, idx = self._new_labelled_graph(data)
        issue_author = {i.number: i.author for i in data.issues if i.author}
        for c in data.comments:
            if c.issue_number and c.author and c.issue_number in issue_author:
                target = issue_author[c.issue_number]
                self._safe_add(graph, idx.get(c.author.id), idx.get(target.id), WEIGHT_COMMENT)
        return graph

    def build_pull_requests_graph(self, data: CollaborationGraph) -> AbstractGraph:
        """Alias de compatibilidade: grafo com comentários em PR + reviews + merges."""
        graph, idx = self._new_labelled_graph(data)
        pr_author = {p.number: p.author for p in data.pull_requests if p.author}
        for c in data.comments:
            if c.pr_number and c.author and c.pr_number in pr_author:
                target = pr_author[c.pr_number]
                self._safe_add(graph, idx.get(c.author.id), idx.get(target.id), WEIGHT_COMMENT)
        for reviewer, author in self._iter_review_edges(data):
            self._safe_add(graph, idx.get(reviewer.id), idx.get(author.id), WEIGHT_REVIEW)
        for merger, author in self._iter_merge_edges(data):
            self._safe_add(graph, idx.get(merger.id), idx.get(author.id), WEIGHT_MERGE)
        return graph

    def build_all_graphs(self, data: CollaborationGraph) -> Dict[str, AbstractGraph]:
        """Compatibilidade: combina aliases antigos com o nome 'total'."""
        return {
            "total": self.build_integrated_graph(data),
            "issues": self.build_issues_graph(data),
            "pull_requests": self.build_pull_requests_graph(data),
        }

    # ---------- estatísticas ----------

    @staticmethod
    def get_graph_statistics(graph: AbstractGraph) -> Dict[str, float]:
        v = graph.get_vertex_count()
        e = graph.get_edge_count()
        max_edges = v * (v - 1)
        density = e / max_edges if max_edges > 0 else 0.0
        return {
            "vertices": v,
            "edges": e,
            "max_edges": max_edges,
            "density": density,
            "is_connected": graph.is_connected(),
            "is_complete": graph.is_complete_graph(),
        }
