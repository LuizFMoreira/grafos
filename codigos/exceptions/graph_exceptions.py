"""
Exceções relacionadas a operações em grafos.

Este módulo define exceções customizadas para validação e operações de grafos,
permitindo tratamento mais específico de erros durante a execução.
"""


class GraphOperationError(Exception):
    """Exceção base para operações em grafos."""
    pass


class InvalidVertexError(GraphOperationError):
    """Levantada quando um vértice inválido é utilizado.

    Vértices válidos devem estar no intervalo [0, vertex_count).
    """

    def __init__(self, vertex: int, vertex_count: int):
        self.vertex = vertex
        self.vertex_count = vertex_count
        msg = (f"Vértice inválido: {vertex}. "
               f"Deve estar no intervalo [0, {vertex_count})")
        super().__init__(msg)


class InvalidEdgeError(GraphOperationError):
    """Levantada quando uma aresta não existe."""

    def __init__(self, u: int, v: int):
        self.u = u
        self.v = v
        super().__init__(f"Aresta {u} → {v} não existe")


class SelfLoopError(GraphOperationError):
    """Levantada quando se tenta criar um laço (self-loop).

    Grafos simples não permitem arestas u → u.
    """

    def __init__(self, vertex: int):
        self.vertex = vertex
        msg = (f"Laço não permitido: {vertex} → {vertex}. "
               f"Grafos simples não permitem self-loops")
        super().__init__(msg)
