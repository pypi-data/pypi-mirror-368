from typing import List, TYPE_CHECKING
import pydot
import uuid

if TYPE_CHECKING:
    from pydot_flow import Chart


class Node:

    def __init__(
        self,
        graph: pydot.Graph,
        src_node_attrs: dict = None,
        src_node: pydot.Node = None,
        chart: "Chart" = None,
        is_connected=True,
    ):
        self._chart = chart
        self._src_node_attrs = {} if src_node_attrs is None else src_node_attrs
        self.graph = graph
        if src_node is None:
            self._src_node = pydot.Node(
                name="node_" + uuid.uuid4().hex, **self._src_node_attrs
            )
            self.graph.add_node(self._src_node)
        else:
            self._src_node = src_node
            if not is_connected:
                self.graph.add_node(self._src_node)

    def get_name(self) -> str:
        return self._src_node.get_name()

    def get_pydot_node(self) -> pydot.Node:
        return self._src_node

    def get_graph(self) -> pydot.Graph:
        return self.graph

    def get_nodes(self) -> List[pydot.Node]:
        nodes = self._chart.get_graph().get_node_list()
        graphs: List[pydot.Subgraph] = self._chart.get_graph().get_subgraph_list()
        for graph in graphs:
            nodes.extend(graph.get_node_list())
            graphs.extend(graph.get_subgraph_list())
        return nodes

    def get_node_by_name(self, name: str) -> pydot.Node:
        nodes = self.get_nodes()
        for node in nodes:
            if node.get_name() == name:
                return node
        return None

    def flow(
        self,
        src_port: str,
        dst_port: str = None,
        dst_node_attrs: dict = None,
        edge_attrs: dict = None,
        graph: pydot.Graph = None,
    ):
        dst_node_attrs = {} if dst_node_attrs is None else dst_node_attrs
        edge_attrs = {} if edge_attrs is None else edge_attrs

        is_connected = False
        if "name" in dst_node_attrs:
            dst_node_name = pydot.quote_if_necessary(dst_node_attrs["name"])
            del dst_node_attrs["name"]
            dst_node = self.get_node_by_name(dst_node_name)
            if dst_node:
                is_connected = True
            else:
                # The Node is not connected; hence, create a new Node.
                dst_node = pydot.Node(name=dst_node_name, **dst_node_attrs)
        else:
            dst_node_name = "node_" + uuid.uuid4().hex
            dst_node = pydot.Node(name=dst_node_name, **dst_node_attrs)

        src_node_name = self._src_node.get_name()

        if dst_port is None:
            dst_port = self._get_dst_port(src_port)
        if "n" in src_port:
            src = src_node_name + ":" + src_port
            dst = dst_node_name + ":" + dst_port
            dir = "forward"
        if "e" in src_port:
            src = src_node_name + ":" + src_port
            dst = dst_node_name + ":" + dst_port
            dir = "forward"
        if "w" in src_port:
            src = dst_node_name + ":" + dst_port
            dst = src_node_name + ":" + src_port
            dir = "back"
        if "s" in src_port:
            src = src_node_name + ":" + src_port
            dst = dst_node_name + ":" + dst_port
            dir = "forward"

        if graph is None:
            graph = self.graph
        else:
            if graph.get_name() == "":
                graph.set_name("graph_" + uuid.uuid4().hex)
            _graphs: List[pydot.Graph] = self._chart.get_graph().get_subgraph_list() + [
                self._chart.get_graph()
            ]
            if not any([_graph.get_name() == graph.get_name() for _graph in _graphs]):
                self.graph.add_subgraph(graph)

        edge = pydot.Edge(src=src, dst=dst, dir=dir, **edge_attrs)
        graph.add_edge(edge)
        return Node(
            graph=graph,
            src_node=dst_node,
            src_node_attrs=dst_node_attrs,
            chart=self._chart,
            is_connected=is_connected,
        )

    def _get_dst_port(self, src_port):
        dst_port = "".join(
            [
                {"n": "s", "s": "n", "w": "e", "e": "w"}.get(direction)
                for direction in list(src_port)
            ]
        )
        return dst_port
