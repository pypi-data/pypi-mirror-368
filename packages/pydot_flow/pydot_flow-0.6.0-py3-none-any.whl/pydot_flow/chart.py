import pydot
from .node import Node


class Chart:
    def __init__(self, *args, **kwargs):
        self._graph = pydot.Dot(*args, **kwargs)

    def create_node(
        self,
        src_node_attrs: dict = None,
    ) -> Node:
        return Node(graph=self._graph, src_node_attrs=src_node_attrs, chart=self)
    
    def get_graph(self) -> pydot.Graph:
        return self._graph
