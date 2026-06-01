"""Cálculo de métricas de rede e centralidade.

Implementação independente de bibliotecas externas de grafo (NetworkX, iGraph,
graph-tool, etc.), conforme exigência do enunciado do TP-ES. Todas as métricas
consomem apenas a API pública de AbstractGraph.

Métricas suportadas (por vértice):
    1. Degree centrality
    2. In-degree / Out-degree
    3. Betweenness centrality      (algoritmo de Brandes)
    4. Closeness centrality        (BFS por fonte)
    5. PageRank                    (power iteration, damping=0.85)
    6. Clustering coefficient      (não-direcionado, local)
    7. Eigenvector centrality      (power iteration sobre A^T)

Métricas globais:
    - Densidade da rede
    - Assortatividade (de grau)
    - Detecção de comunidades por Label Propagation + modularidade Q
    - Bridging ties (arestas entre comunidades distintas)
"""

from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
import math

from ..models import User, MetricsResult
from ..core.graph import AbstractGraph


class MetricsService:
    """Calcula métricas de rede para grafos de colaboração.

    Não utiliza bibliotecas externas de grafo — todos os algoritmos são
    implementados aqui sobre `AbstractGraph`.
    """

    PAGERANK_DAMPING = 0.85
    PAGERANK_TOL = 1e-6
    PAGERANK_MAX_ITER = 100
    EIGEN_TOL = 1e-6
    EIGEN_MAX_ITER = 200

    def __init__(self, graph: AbstractGraph, users: List[User]):
        if not isinstance(users, list) or len(users) == 0:
            raise ValueError("users must be non-empty list")
        if graph.get_vertex_count() != len(users):
            raise ValueError(
                f"Graph has {graph.get_vertex_count()} vertices "
                f"but {len(users)} users provided"
            )
        self.graph = graph
        self.users = users
        self.n = graph.get_vertex_count()

        # Caches de estrutura (consultados várias vezes).
        self._successors: Dict[int, List[int]] = {
            v: self._collect_successors(v) for v in range(self.n)
        }
        self._predecessors: Dict[int, List[int]] = {
            v: self._collect_predecessors(v) for v in range(self.n)
        }

    # ------------------------------------------------------------------
    # Auxiliares de estrutura
    # ------------------------------------------------------------------

    def _collect_successors(self, v: int) -> List[int]:
        getter = getattr(self.graph, "get_successors", None)
        if callable(getter):
            return list(getter(v))
        return [u for u in range(self.n) if self.graph.has_edge(v, u)]

    def _collect_predecessors(self, v: int) -> List[int]:
        getter = getattr(self.graph, "get_predecessors", None)
        if callable(getter):
            return list(getter(v))
        return [u for u in range(self.n) if self.graph.has_edge(u, v)]

    def _undirected_neighbors(self, v: int) -> List[int]:
        return list(set(self._successors[v]) | set(self._predecessors[v]))

    # ------------------------------------------------------------------
    # API pública agregadora
    # ------------------------------------------------------------------

    def calculate_all_metrics(self) -> List[MetricsResult]:
        degree = self._degree_centrality()
        in_deg = self._in_degree()
        out_deg = self._out_degree()
        between = self._betweenness_centrality()
        close = self._closeness_centrality()
        pr = self._pagerank()
        clust = self._clustering_coefficient()
        eig = self._eigenvector_centrality()

        results = []
        for i, user in enumerate(self.users):
            results.append(MetricsResult(
                user=user,
                degree_centrality=_clip01(degree.get(i, 0.0)),
                in_degree=in_deg.get(i, 0),
                out_degree=out_deg.get(i, 0),
                betweenness_centrality=_clip01(between.get(i, 0.0)),
                closeness_centrality=_clip01(close.get(i, 0.0)),
                pagerank=max(0.0, pr.get(i, 0.0)),
                clustering_coefficient=_clip01(clust.get(i, 0.0)),
                eigenvector_centrality=_clip01(eig.get(i, 0.0)),
            ))
        return results

    # ------------------------------------------------------------------
    # Centralidades simples (degree)
    # ------------------------------------------------------------------

    def _degree_centrality(self) -> Dict[int, float]:
        if self.n <= 1:
            return {i: 0.0 for i in range(self.n)}
        denom = 2 * (self.n - 1)
        return {
            v: (self.graph.get_vertex_in_degree(v) + self.graph.get_vertex_out_degree(v)) / denom
            for v in range(self.n)
        }

    def _in_degree(self) -> Dict[int, int]:
        return {v: self.graph.get_vertex_in_degree(v) for v in range(self.n)}

    def _out_degree(self) -> Dict[int, int]:
        return {v: self.graph.get_vertex_out_degree(v) for v in range(self.n)}

    # ------------------------------------------------------------------
    # Betweenness (Brandes)
    # ------------------------------------------------------------------

    def _betweenness_centrality(self) -> Dict[int, float]:
        """Brandes (2001) para grafos direcionados não-ponderados.

        Retorna betweenness normalizado por (n-1)(n-2).
        """
        cb = {v: 0.0 for v in range(self.n)}
        if self.n < 3:
            return cb

        for s in range(self.n):
            stack: List[int] = []
            pred: Dict[int, List[int]] = {v: [] for v in range(self.n)}
            sigma = [0] * self.n
            dist = [-1] * self.n
            sigma[s] = 1
            dist[s] = 0
            queue = deque([s])

            while queue:
                v = queue.popleft()
                stack.append(v)
                for w in self._successors[v]:
                    if dist[w] < 0:
                        queue.append(w)
                        dist[w] = dist[v] + 1
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        pred[w].append(v)

            delta = [0.0] * self.n
            while stack:
                w = stack.pop()
                for v in pred[w]:
                    if sigma[w]:
                        delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    cb[w] += delta[w]

        norm = (self.n - 1) * (self.n - 2)
        if norm > 0:
            cb = {v: c / norm for v, c in cb.items()}
        return cb

    # ------------------------------------------------------------------
    # Closeness
    # ------------------------------------------------------------------

    def _closeness_centrality(self) -> Dict[int, float]:
        """Closeness = (alcançados-1) / soma das distâncias, ponderado pela
        fração de vértices alcançáveis (Wasserman-Faust)."""
        close = {v: 0.0 for v in range(self.n)}
        if self.n <= 1:
            return close

        for v in range(self.n):
            dist = self._bfs_distances(v)
            reachable = [d for d in dist if d > 0]
            if not reachable:
                continue
            total = sum(reachable)
            r = len(reachable)
            if total > 0:
                close[v] = (r / total) * (r / (self.n - 1))
        return close

    def _bfs_distances(self, source: int) -> List[int]:
        dist = [-1] * self.n
        dist[source] = 0
        queue = deque([source])
        while queue:
            v = queue.popleft()
            for u in self._successors[v]:
                if dist[u] < 0:
                    dist[u] = dist[v] + 1
                    queue.append(u)
        # devolver 0 para fontes (não conta no closeness), -1 vira 0 também
        return [d if d > 0 else 0 for d in dist]

    # ------------------------------------------------------------------
    # PageRank (power iteration)
    # ------------------------------------------------------------------

    def _pagerank(self) -> Dict[int, float]:
        if self.n == 0:
            return {}
        rank = {v: 1.0 / self.n for v in range(self.n)}
        out_weight_sum = self._out_weight_sums()

        for _ in range(self.PAGERANK_MAX_ITER):
            new_rank = {v: (1 - self.PAGERANK_DAMPING) / self.n for v in range(self.n)}
            dangling = 0.0
            for v in range(self.n):
                if out_weight_sum[v] == 0:
                    dangling += rank[v]
            for v in range(self.n):
                contrib = self.PAGERANK_DAMPING * dangling / self.n
                new_rank[v] += contrib
                for succ in self._successors[v]:
                    if out_weight_sum[v] > 0:
                        w = self.graph.get_edge_weight(v, succ)
                        new_rank[succ] += self.PAGERANK_DAMPING * rank[v] * w / out_weight_sum[v]
            diff = sum(abs(new_rank[v] - rank[v]) for v in range(self.n))
            rank = new_rank
            if diff < self.PAGERANK_TOL:
                break
        return rank

    def _out_weight_sums(self) -> Dict[int, float]:
        sums = {}
        for v in range(self.n):
            total = 0.0
            for s in self._successors[v]:
                total += self.graph.get_edge_weight(v, s)
            sums[v] = total
        return sums

    # ------------------------------------------------------------------
    # Clustering coefficient (versão local não-direcionada)
    # ------------------------------------------------------------------

    def _clustering_coefficient(self) -> Dict[int, float]:
        adj = {v: set(self._undirected_neighbors(v)) for v in range(self.n)}
        result = {}
        for v in range(self.n):
            neigh = adj[v]
            k = len(neigh)
            if k < 2:
                result[v] = 0.0
                continue
            links = 0
            neigh_list = list(neigh)
            for i in range(len(neigh_list)):
                ni = neigh_list[i]
                for j in range(i + 1, len(neigh_list)):
                    nj = neigh_list[j]
                    if nj in adj[ni]:
                        links += 1
            result[v] = (2 * links) / (k * (k - 1))
        return result

    # ------------------------------------------------------------------
    # Eigenvector centrality (power iteration sobre A^T)
    # ------------------------------------------------------------------

    def _eigenvector_centrality(self) -> Dict[int, float]:
        if self.n == 0:
            return {}
        x = [1.0 / math.sqrt(self.n)] * self.n
        for _ in range(self.EIGEN_MAX_ITER):
            new_x = [0.0] * self.n
            for v in range(self.n):
                for u in self._predecessors[v]:
                    w = self.graph.get_edge_weight(u, v)
                    new_x[v] += w * x[u]
            norm = math.sqrt(sum(c * c for c in new_x))
            if norm == 0:
                return {v: 0.0 for v in range(self.n)}
            new_x = [c / norm for c in new_x]
            diff = sum(abs(new_x[i] - x[i]) for i in range(self.n))
            x = new_x
            if diff < self.EIGEN_TOL:
                break
        return {v: x[v] for v in range(self.n)}

    # ------------------------------------------------------------------
    # Métricas globais
    # ------------------------------------------------------------------

    def density(self) -> float:
        """Densidade do grafo direcionado: m / (n·(n-1))."""
        if self.n < 2:
            return 0.0
        return self.graph.get_edge_count() / (self.n * (self.n - 1))

    def degree_assortativity(self) -> float:
        """Assortatividade de grau (Pearson sobre extremos das arestas).

        Considera o grau total (in+out) de cada ponta. Retorna 0.0 se não há
        arestas ou se a variância é zero (ex.: regular).
        """
        edges: List[Tuple[int, int]] = []
        for u in range(self.n):
            for v in self._successors[u]:
                edges.append((u, v))
        if not edges:
            return 0.0
        total_degree = [
            self.graph.get_vertex_in_degree(v) + self.graph.get_vertex_out_degree(v)
            for v in range(self.n)
        ]
        m = len(edges)
        sx = sum(total_degree[u] for u, _ in edges)
        sy = sum(total_degree[v] for _, v in edges)
        mean_x = sx / m
        mean_y = sy / m
        num = sum((total_degree[u] - mean_x) * (total_degree[v] - mean_y) for u, v in edges)
        denx = math.sqrt(sum((total_degree[u] - mean_x) ** 2 for u, _ in edges))
        deny = math.sqrt(sum((total_degree[v] - mean_y) ** 2 for _, v in edges))
        if denx == 0 or deny == 0:
            return 0.0
        return num / (denx * deny)

    def detect_communities(self, max_iter: int = 100) -> Dict[int, int]:
        """Label Propagation Algorithm (LPA) sobre o grafo não-direcionado.

        Cada vértice começa em sua própria comunidade; a cada iteração
        adota o rótulo dominante entre vizinhos (desempate determinístico).
        Retorna {vertex_index → community_id}.
        """
        labels = {v: v for v in range(self.n)}
        if self.n == 0:
            return labels
        for _ in range(max_iter):
            changed = False
            order = list(range(self.n))
            for v in order:
                neigh = self._undirected_neighbors(v)
                if not neigh:
                    continue
                counts: Dict[int, int] = defaultdict(int)
                for u in neigh:
                    counts[labels[u]] += 1
                best_count = max(counts.values())
                best_labels = [lbl for lbl, c in counts.items() if c == best_count]
                # desempate: menor rótulo (estabilidade)
                new_label = min(best_labels)
                if labels[v] != new_label:
                    labels[v] = new_label
                    changed = True
            if not changed:
                break
        return labels

    def modularity(self, partition: Optional[Dict[int, int]] = None) -> float:
        """Modularidade Q (Newman) para um grafo direcionado ponderado.

        Q = (1/m) Σ_{ij} [A_ij − (k_i^out * k_j^in)/m] δ(c_i, c_j)
        Considera pesos das arestas. Se `partition` for None, usa as
        comunidades de `detect_communities`.
        """
        if partition is None:
            partition = self.detect_communities()
        out_strength = {v: 0.0 for v in range(self.n)}
        in_strength = {v: 0.0 for v in range(self.n)}
        m = 0.0
        for u in range(self.n):
            for v in self._successors[u]:
                w = self.graph.get_edge_weight(u, v)
                out_strength[u] += w
                in_strength[v] += w
                m += w
        if m == 0:
            return 0.0
        q = 0.0
        for u in range(self.n):
            for v in range(self.n):
                if partition.get(u) != partition.get(v):
                    continue
                a_uv = self.graph.get_edge_weight(u, v) if self.graph.has_edge(u, v) else 0.0
                expected = (out_strength[u] * in_strength[v]) / m
                q += (a_uv - expected)
        return q / m

    def bridging_ties(
        self, partition: Optional[Dict[int, int]] = None
    ) -> List[Tuple[int, int, float]]:
        """Lista de arestas que cruzam comunidades distintas.

        Retorna lista de (u, v, peso) ordenada por peso decrescente.
        Útil para identificar "pontes" entre comunidades.
        """
        if partition is None:
            partition = self.detect_communities()
        out: List[Tuple[int, int, float]] = []
        for u in range(self.n):
            for v in self._successors[u]:
                if partition.get(u) != partition.get(v):
                    out.append((u, v, self.graph.get_edge_weight(u, v)))
        out.sort(key=lambda t: t[2], reverse=True)
        return out

    # ------------------------------------------------------------------
    # Conveniências
    # ------------------------------------------------------------------

    def get_top_by_metric(self, metric_name: str, top_n: int = 10) -> List[tuple]:
        results = self.calculate_all_metrics()
        metric_map = {
            "pagerank": "pagerank",
            "degree_centrality": "degree_centrality",
            "betweenness": "betweenness_centrality",
            "closeness": "closeness_centrality",
            "clustering": "clustering_coefficient",
            "eigenvector": "eigenvector_centrality",
            "in_degree": "in_degree",
            "out_degree": "out_degree",
        }
        if metric_name not in metric_map:
            raise ValueError(f"Unknown metric: {metric_name}")
        attr = metric_map[metric_name]
        sorted_results = sorted(results, key=lambda r: getattr(r, attr), reverse=True)
        return [(r.user, getattr(r, attr)) for r in sorted_results[:top_n]]

    def get_metrics_summary(self) -> Dict[str, float]:
        results = self.calculate_all_metrics()
        if not results:
            return {}

        def avg(values):
            return sum(values) / len(values) if values else 0.0

        deg = [r.degree_centrality for r in results]
        bet = [r.betweenness_centrality for r in results]
        clo = [r.closeness_centrality for r in results]
        prs = [r.pagerank for r in results]
        clu = [r.clustering_coefficient for r in results]
        eig = [r.eigenvector_centrality for r in results]

        partition = self.detect_communities()
        n_communities = len(set(partition.values())) if partition else 0

        return {
            "avg_degree_centrality": avg(deg),
            "max_degree_centrality": max(deg) if deg else 0.0,
            "min_degree_centrality": min(deg) if deg else 0.0,
            "avg_betweenness": avg(bet),
            "max_betweenness": max(bet) if bet else 0.0,
            "avg_closeness": avg(clo),
            "max_closeness": max(clo) if clo else 0.0,
            "avg_pagerank": avg(prs),
            "max_pagerank": max(prs) if prs else 0.0,
            "avg_clustering": avg(clu),
            "max_clustering": max(clu) if clu else 0.0,
            "avg_eigenvector": avg(eig),
            "max_eigenvector": max(eig) if eig else 0.0,
            "density": self.density(),
            "assortativity": self.degree_assortativity(),
            "n_communities": n_communities,
            "modularity": self.modularity(partition),
            "n_bridging_ties": len(self.bridging_ties(partition)),
        }


def _clip01(x: float) -> float:
    """Limita um valor a [0, 1] (evita erros de validação por ruído numérico)."""
    if x < 0:
        return 0.0
    if x > 1:
        return 1.0
    return x
