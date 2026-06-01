"""Testes das métricas reimplementadas sem NetworkX.

Cenários pequenos com valores conferidos analiticamente.
"""
import math

import pytest

from codigos.core.graph import AdjacencyListGraph
from codigos.models import User
from codigos.services.metrics import MetricsService


def _users(n):
    return [User(id=i + 1, login=f"u{i}") for i in range(n)]


# ----- Estrutura: ciclo dirigido 0→1→2→0 -----

@pytest.fixture
def cycle3():
    g = AdjacencyListGraph(3)
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(2, 0)
    return MetricsService(g, _users(3))


def test_degree_centrality_cycle(cycle3):
    # cada vértice: in=1, out=1, total=2; denom=2*(n-1)=4 → 0.5
    d = cycle3._degree_centrality()
    assert all(v == pytest.approx(0.5) for v in d.values())


def test_density_cycle(cycle3):
    # 3 arestas, max = 3*2=6 → densidade 0.5
    assert cycle3.density() == pytest.approx(0.5)


def test_closeness_cycle(cycle3):
    # Em ciclo dirigido, todo vértice alcança outros 2 com somas 1+2=3
    # closeness = (2/3) * (2/2) = 0.6666...
    c = cycle3._closeness_centrality()
    for v in range(3):
        assert c[v] == pytest.approx(2 / 3, rel=1e-3)


def test_pagerank_sums_to_one_uniform_for_cycle(cycle3):
    pr = cycle3._pagerank()
    s = sum(pr.values())
    assert s == pytest.approx(1.0, rel=1e-3)
    # ciclo simétrico → todos com mesmo rank
    vals = list(pr.values())
    for v in vals:
        assert v == pytest.approx(1 / 3, rel=1e-2)


def test_betweenness_cycle(cycle3):
    # Em ciclo dirigido de 3 nós, cada par tem caminho único único intermediário
    # Brandes normalizado por (n-1)(n-2)=2 → cada vértice deve ter 0.5
    b = cycle3._betweenness_centrality()
    for v in range(3):
        assert b[v] == pytest.approx(0.5, rel=1e-3)


# ----- Star (estrela): centro 0 com folhas 1,2,3 ligadas em ambos sentidos -----

@pytest.fixture
def star4():
    g = AdjacencyListGraph(4)
    for leaf in (1, 2, 3):
        g.add_edge(0, leaf)
        g.add_edge(leaf, 0)
    return MetricsService(g, _users(4))


def test_star_degree_centrality(star4):
    d = star4._degree_centrality()
    # centro: in=3,out=3,total=6, denom=6 → 1.0
    assert d[0] == pytest.approx(1.0)
    # folhas: in=1,out=1,total=2, denom=6 → 1/3
    for leaf in (1, 2, 3):
        assert d[leaf] == pytest.approx(1 / 3, rel=1e-3)


def test_star_betweenness_center_dominates(star4):
    b = star4._betweenness_centrality()
    # centro intermedeia todos os caminhos entre folhas: máx 1.0; folhas: 0
    assert b[0] == pytest.approx(1.0, rel=1e-3)
    for leaf in (1, 2, 3):
        assert b[leaf] == pytest.approx(0.0, abs=1e-9)


def test_star_clustering_zero(star4):
    # vizinhos do centro não se conectam entre si (apenas via centro) → 0
    c = star4._clustering_coefficient()
    assert c[0] == pytest.approx(0.0)


# ----- Eigenvector centrality em ciclo simétrico converge p/ uniforme -----

def test_eigenvector_cycle_uniform(cycle3):
    ev = cycle3._eigenvector_centrality()
    s = math.sqrt(sum(v * v for v in ev.values()))
    assert s == pytest.approx(1.0, rel=1e-3)
    for v in ev.values():
        assert v == pytest.approx(1 / math.sqrt(3), rel=1e-2)


# ----- Comunidades / modularidade / bridging -----

def test_two_disjoint_triangles_have_two_communities():
    # Triângulo A: 0,1,2; Triângulo B: 3,4,5; sem ponte
    g = AdjacencyListGraph(6)
    for u, v in [(0, 1), (1, 2), (2, 0), (1, 0), (2, 1), (0, 2)]:
        g.add_edge(u, v)
    for u, v in [(3, 4), (4, 5), (5, 3), (4, 3), (5, 4), (3, 5)]:
        g.add_edge(u, v)
    svc = MetricsService(g, _users(6))
    part = svc.detect_communities()
    # deve dar 2 grupos distintos
    groups = set(part.values())
    assert len(groups) == 2
    # modularidade positiva (estrutura claramente modular)
    assert svc.modularity(part) > 0.3


def test_bridging_ties_detected():
    # Dois triângulos + uma única aresta-ponte 2→3. Forçamos a partição
    # manualmente para validar APENAS a lógica de bridging_ties (LPA é
    # heurística e pode variar conforme o desempate).
    g = AdjacencyListGraph(6)
    for u, v in [(0, 1), (1, 2), (2, 0), (1, 0), (2, 1), (0, 2)]:
        g.add_edge(u, v, 1.0)
    for u, v in [(3, 4), (4, 5), (5, 3), (4, 3), (5, 4), (3, 5)]:
        g.add_edge(u, v, 1.0)
    g.add_edge(2, 3, 7.0)
    svc = MetricsService(g, _users(6))
    partition = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1}
    bridges = svc.bridging_ties(partition)
    assert (2, 3, 7.0) in bridges
    # como é a única ponte, é a primeira (e única)
    assert bridges[0][0:2] == (2, 3)


def test_assortativity_regular_graph_returns_zero():
    # ciclo regular (todos com grau 2 total) → variância zero → 0
    g = AdjacencyListGraph(4)
    for u, v in [(0, 1), (1, 2), (2, 3), (3, 0)]:
        g.add_edge(u, v)
    svc = MetricsService(g, _users(4))
    assert svc.degree_assortativity() == pytest.approx(0.0)


def test_metrics_summary_has_new_keys():
    g = AdjacencyListGraph(3)
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    svc = MetricsService(g, _users(3))
    summary = svc.get_metrics_summary()
    for key in ("density", "assortativity", "n_communities", "modularity", "n_bridging_ties"):
        assert key in summary
