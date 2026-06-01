"""Demonstração da API de grafos exigida pelo enunciado do TP-ES.

Exercita os 19 métodos obrigatórios definidos em `AbstractGraph` com prints
didáticos, permitindo ao avaliador verificar visualmente o comportamento de
cada operação nas duas implementações concretas:

    - AdjacencyListGraph
    - AdjacencyMatrixGraph

Uso:
    py -3 -m codigos.app.api_demo
"""

import os
import sys
import tempfile
from typing import Type

# Garante UTF-8 no Windows (cp1252 não suporta '→', acentos etc.)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ..core.graph import AbstractGraph, AdjacencyListGraph, AdjacencyMatrixGraph
from ..exceptions.graph_exceptions import (
    InvalidEdgeError,
    InvalidVertexError,
    SelfLoopError,
)


SEP = "-" * 72


def banner(text: str) -> None:
    print()
    print("=" * 72)
    print(f"  {text}")
    print("=" * 72)


def section(title: str) -> None:
    print(f"\n>>> {title}")
    print(SEP)


def show(label: str, value) -> None:
    print(f"  {label:<48} = {value}")


def demonstrate(impl: Type[AbstractGraph]) -> None:
    banner(f"Demonstração da API — {impl.__name__}")

    section("1) Construtor + estado inicial")
    g = impl(5)
    show("getVertexCount()", g.get_vertex_count())
    show("getEdgeCount()", g.get_edge_count())
    show("isEmptyGraph()", g.is_empty_graph())

    section("2) setVertexLabel / setVertexWeight / getVertexWeight")
    nomes = ["ana", "bruno", "carla", "diego", "elisa"]
    for i, nome in enumerate(nomes):
        g.set_vertex_label(i, nome)
        g.set_vertex_weight(i, 1.0 + i * 0.5)
    for i in range(5):
        show(f"vértice {i} (label, weight)", (g.get_vertex_label(i), g.get_vertex_weight(i)))

    section("3) addEdge — construindo grafo com arestas ponderadas")
    arestas = [(0, 1, 2.0), (0, 2, 3.0), (1, 2, 1.5),
               (2, 3, 4.0), (3, 4, 5.0), (4, 0, 2.5)]
    for u, v, w in arestas:
        g.add_edge(u, v, weight=w)
        print(f"  add_edge({u} -> {v}, weight={w})")
    show("getEdgeCount() após inserções", g.get_edge_count())

    section("4) addEdge é idempotente (acumula peso)")
    print("  Antes: get_edge_weight(0, 1) =", g.get_edge_weight(0, 1))
    g.add_edge(0, 1, weight=10.0)
    print("  Após add_edge(0, 1, weight=10.0): get_edge_weight(0, 1) =", g.get_edge_weight(0, 1))
    show("getEdgeCount() (não muda)", g.get_edge_count())

    section("5) addEdge rejeita laços (self-loops)")
    try:
        g.add_edge(2, 2)
    except SelfLoopError as e:
        print(f"  SelfLoopError capturada: {e}")

    section("6) addEdge / has_edge validam vértices inválidos")
    try:
        g.has_edge(0, 99)
    except InvalidVertexError as e:
        print(f"  InvalidVertexError capturada: {e}")

    section("7) hasEdge / isSucessor / isPredessor")
    show("has_edge(0, 1)", g.has_edge(0, 1))
    show("has_edge(1, 0)", g.has_edge(1, 0))
    show("is_successor(0, 1)  (1 é sucessor de 0?)", g.is_successor(0, 1))
    show("is_predecessor(1, 0) (0 é predecessor de 1?)", g.is_predecessor(1, 0))

    section("8) isDivergent / isConvergent / isIncident")
    show("is_divergent((0,1),(0,2))", g.is_divergent(0, 1, 0, 2))
    show("is_convergent((0,2),(1,2))", g.is_convergent(0, 2, 1, 2))
    show("is_incident(0, 1, 0)", g.is_incident(0, 1, 0))
    show("is_incident(0, 1, 3)", g.is_incident(0, 1, 3))

    section("9) getVertexInDegree / getVertexOutDegree")
    for v in range(5):
        show(f"vértice {v}: (in, out)",
             (g.get_vertex_in_degree(v), g.get_vertex_out_degree(v)))

    section("10) setEdgeWeight / getEdgeWeight")
    g.set_edge_weight(0, 2, 99.0)
    show("get_edge_weight(0, 2) após set=99", g.get_edge_weight(0, 2))

    section("11) removeEdge (e remoção de aresta inexistente)")
    g.remove_edge(0, 2)
    show("get_edge_count() após remoção", g.get_edge_count())
    show("has_edge(0, 2) após remoção", g.has_edge(0, 2))
    try:
        g.remove_edge(0, 2)
    except InvalidEdgeError as e:
        print(f"  InvalidEdgeError esperada ao remover de novo: {e}")

    section("12) isConnected (forte) e isCompleteGraph e isEmptyGraph")
    show("is_connected() (este grafo)", g.is_connected())
    show("is_complete_graph()", g.is_complete_graph())
    show("is_empty_graph()", g.is_empty_graph())

    section("13) Exemplo de grafo completo K3 dirigido")
    k3 = impl(3)
    for u, v in [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]:
        k3.add_edge(u, v)
    show("K3 dirigido — is_complete_graph()", k3.is_complete_graph())
    show("K3 dirigido — get_edge_count()", k3.get_edge_count())

    section("14) exportToGEPHI — três formatos")
    out_dir = os.path.join(tempfile.gettempdir(), f"api_demo_{impl.__name__.lower()}")
    os.makedirs(out_dir, exist_ok=True)
    for fmt in ("gexf", "graphml", "csv"):
        path = os.path.join(out_dir, f"grafo_{fmt}")
        g.export_to_gephi(path, format=fmt)
        print(f"  exportado em formato {fmt:<7} -> '{path}'")
    print(f"\n  (Arquivos gravados em {out_dir})")


def main() -> int:
    demonstrate(AdjacencyListGraph)
    demonstrate(AdjacencyMatrixGraph)
    banner("Demonstração concluída — todos os 19 métodos da API foram exercitados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
