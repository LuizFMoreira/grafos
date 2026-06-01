"""Cobertura unitária dos 19 métodos obrigatórios da API de grafos.

Executa o mesmo conjunto de cenários contra AdjacencyListGraph e
AdjacencyMatrixGraph via parametrização, garantindo paridade entre as
duas implementações.
"""
import os

import pytest

from codigos.core.graph import AdjacencyListGraph, AdjacencyMatrixGraph
from codigos.exceptions.graph_exceptions import (
    InvalidEdgeError,
    InvalidVertexError,
    SelfLoopError,
)


GRAPH_IMPLS = [AdjacencyListGraph, AdjacencyMatrixGraph]


@pytest.fixture(params=GRAPH_IMPLS, ids=lambda c: c.__name__)
def graph_cls(request):
    return request.param


# ----- Construtor -----

def test_constructor_rejects_zero_or_negative(graph_cls):
    with pytest.raises(ValueError):
        graph_cls(0)
    with pytest.raises(ValueError):
        graph_cls(-1)


def test_constructor_initial_state(graph_cls):
    g = graph_cls(5)
    assert g.get_vertex_count() == 5
    assert g.get_edge_count() == 0
    assert g.is_empty_graph() is True


# ----- add_edge / has_edge / remove_edge -----

def test_add_edge_rejects_self_loop(graph_cls):
    g = graph_cls(3)
    with pytest.raises(SelfLoopError):
        g.add_edge(1, 1)


def test_add_edge_rejects_invalid_vertex(graph_cls):
    g = graph_cls(3)
    with pytest.raises(InvalidVertexError):
        g.add_edge(0, 5)
    with pytest.raises(InvalidVertexError):
        g.add_edge(-1, 0)


def test_add_edge_idempotent_accumulates_weight(graph_cls):
    g = graph_cls(3)
    g.add_edge(0, 1, 2.0)
    g.add_edge(0, 1, 3.0)
    assert g.get_edge_count() == 1
    assert g.get_edge_weight(0, 1) == pytest.approx(5.0)


def test_add_edge_rejects_negative_weight(graph_cls):
    g = graph_cls(3)
    with pytest.raises(ValueError):
        g.add_edge(0, 1, -1.0)


def test_has_edge_truthiness(graph_cls):
    g = graph_cls(3)
    g.add_edge(0, 1)
    assert g.has_edge(0, 1) is True
    assert g.has_edge(1, 0) is False


def test_remove_edge_decreases_count(graph_cls):
    g = graph_cls(3)
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.remove_edge(0, 1)
    assert g.get_edge_count() == 1
    assert g.has_edge(0, 1) is False


def test_remove_edge_raises_when_absent(graph_cls):
    g = graph_cls(3)
    with pytest.raises(InvalidEdgeError):
        g.remove_edge(0, 1)


# ----- is_successor / is_predecessor -----

def test_successor_predecessor(graph_cls):
    g = graph_cls(3)
    g.add_edge(0, 2)
    assert g.is_successor(0, 2) is True
    assert g.is_successor(2, 0) is False
    assert g.is_predecessor(2, 0) is True
    assert g.is_predecessor(0, 2) is False


# ----- is_divergent / is_convergent / is_incident (regressão do bug do _validate_vertices) -----

def test_is_divergent(graph_cls):
    g = graph_cls(4)
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.add_edge(3, 2)
    assert g.is_divergent(0, 1, 0, 2) is True
    assert g.is_divergent(0, 1, 3, 2) is False


def test_is_convergent(graph_cls):
    g = graph_cls(4)
    g.add_edge(0, 2)
    g.add_edge(3, 2)
    g.add_edge(0, 1)
    assert g.is_convergent(0, 2, 3, 2) is True
    assert g.is_convergent(0, 1, 0, 2) is False


def test_is_incident(graph_cls):
    g = graph_cls(3)
    g.add_edge(0, 1)
    assert g.is_incident(0, 1, 0) is True
    assert g.is_incident(0, 1, 1) is True
    assert g.is_incident(0, 1, 2) is False


def test_relations_validate_all_indices(graph_cls):
    g = graph_cls(3)
    with pytest.raises(InvalidVertexError):
        g.is_divergent(0, 1, 0, 99)
    with pytest.raises(InvalidVertexError):
        g.is_convergent(0, 1, 99, 1)
    with pytest.raises(InvalidVertexError):
        g.is_incident(0, 1, 99)


# ----- Graus -----

def test_in_out_degree(graph_cls):
    g = graph_cls(4)
    g.add_edge(0, 1)
    g.add_edge(2, 1)
    g.add_edge(3, 1)
    g.add_edge(1, 0)
    assert g.get_vertex_in_degree(1) == 3
    assert g.get_vertex_out_degree(1) == 1
    assert g.get_vertex_in_degree(0) == 1
    assert g.get_vertex_out_degree(0) == 1
    assert g.get_vertex_in_degree(3) == 0


def test_degree_invalid_vertex(graph_cls):
    g = graph_cls(3)
    with pytest.raises(InvalidVertexError):
        g.get_vertex_in_degree(99)
    with pytest.raises(InvalidVertexError):
        g.get_vertex_out_degree(-1)


# ----- Pesos -----

def test_vertex_weight_set_get(graph_cls):
    g = graph_cls(3)
    g.set_vertex_weight(1, 4.2)
    assert g.get_vertex_weight(1) == pytest.approx(4.2)


def test_vertex_weight_rejects_negative(graph_cls):
    g = graph_cls(3)
    with pytest.raises(ValueError):
        g.set_vertex_weight(0, -1.0)


def test_edge_weight_set_get(graph_cls):
    g = graph_cls(3)
    g.add_edge(0, 1, 1.0)
    g.set_edge_weight(0, 1, 7.5)
    assert g.get_edge_weight(0, 1) == pytest.approx(7.5)


def test_edge_weight_on_missing_edge_raises(graph_cls):
    g = graph_cls(3)
    with pytest.raises(InvalidEdgeError):
        g.get_edge_weight(0, 1)
    with pytest.raises(InvalidEdgeError):
        g.set_edge_weight(0, 1, 3.0)


# ----- is_connected (forte) -----

def test_is_connected_strongly_connected_cycle(graph_cls):
    g = graph_cls(3)
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(2, 0)
    assert g.is_connected() is True


def test_is_connected_disconnected(graph_cls):
    g = graph_cls(3)
    g.add_edge(0, 1)
    assert g.is_connected() is False


def test_is_connected_one_way_only(graph_cls):
    g = graph_cls(3)
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    # caminho 0→1→2 existe, mas não de volta → não é fortemente conectado
    assert g.is_connected() is False


# ----- is_complete_graph / is_empty_graph -----

def test_is_complete_graph(graph_cls):
    g = graph_cls(3)
    pares = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
    for u, v in pares:
        g.add_edge(u, v)
    assert g.is_complete_graph() is True
    assert g.get_edge_count() == 6


def test_is_complete_graph_incomplete(graph_cls):
    g = graph_cls(3)
    g.add_edge(0, 1)
    assert g.is_complete_graph() is False


def test_is_empty_graph(graph_cls):
    g = graph_cls(3)
    assert g.is_empty_graph() is True
    g.add_edge(0, 1)
    assert g.is_empty_graph() is False


# ----- export_to_gephi -----

@pytest.mark.parametrize("fmt,ext", [("gexf", ".gexf"), ("graphml", ".graphml")])
def test_export_to_gephi_creates_file(graph_cls, tmp_path, fmt, ext):
    g = graph_cls(3)
    g.add_edge(0, 1, 1.5)
    g.add_edge(1, 2, 2.5)
    g.set_vertex_label(0, "ana")
    g.set_vertex_label(1, "bruno")
    out = tmp_path / "grafo"
    g.export_to_gephi(str(out), format=fmt)
    arquivo = out.with_suffix(ext)
    assert arquivo.exists()
    conteudo = arquivo.read_text(encoding="utf-8")
    assert "source=\"0\"" in conteudo and "target=\"1\"" in conteudo


def test_export_to_gephi_csv_creates_two_files(graph_cls, tmp_path):
    g = graph_cls(2)
    g.add_edge(0, 1, 3.0)
    base = tmp_path / "grafo"
    g.export_to_gephi(str(base), format="csv")
    assert (tmp_path / "grafo_nodes.csv").exists()
    assert (tmp_path / "grafo_edges.csv").exists()


def test_export_to_gephi_rejects_unknown_format(graph_cls, tmp_path):
    g = graph_cls(2)
    g.add_edge(0, 1)
    with pytest.raises(ValueError):
        g.export_to_gephi(str(tmp_path / "x"), format="dot")
