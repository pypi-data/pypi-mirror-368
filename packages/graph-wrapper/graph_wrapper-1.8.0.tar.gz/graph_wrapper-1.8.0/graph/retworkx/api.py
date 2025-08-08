from __future__ import annotations

from itertools import product
from typing import Optional

import rustworkx

from graph.retworkx.digraph import Edge, EdgeKey, Node, NodeID, _RetworkXDiGraph
from graph.retworkx.str_digraph import RetworkXStrDiGraph


def digraph_all_simple_paths(
    g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge],
    source: NodeID,
    target: NodeID,
    min_depth: Optional[int] = None,
    cutoff: Optional[int] = None,
) -> list[list[Edge]]:
    """
    Return all simple paths between 2 nodes in a PyDiGraph object
    A simple path is a path with no repeated nodes.

    Args:
        g: The graph to find the path in
        source: The node index to find the paths from
        target: The node index to find the paths to
        min_depth: The minimum depth of the path to include in the output
            list of paths. By default all paths are included regardless of depth,
            set to None will behave like the default.
        cutoff: The maximum depth of path (number of edges) to include in the output list
            of paths. By default includes all paths regardless of depth, setting to
            None will behave like default.

    Return a list of lists where each inner list is a path containing edges
    """
    if cutoff is not None:
        cutoff += 1
    if isinstance(g, RetworkXStrDiGraph):
        source = g.idmap[source]
        target = g.idmap[target]

    output = []
    visited_paths = set()
    for nodes in rustworkx.digraph_all_simple_paths(
        g._graph, source, target, min_depth, cutoff
    ):
        path_id = tuple(nodes)
        if path_id in visited_paths:
            continue

        visited_paths.add(path_id)
        path = []
        for i in range(1, len(nodes)):
            path.append(g._graph.get_all_edge_data(nodes[i - 1], nodes[i]))
        for x in product(*path):
            output.append(list(x))
    return output


def dag_longest_path(g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge]) -> list[NodeID]:
    """
    Return the longest path in a DAG

    Args:
        g: The graph to find the longest path in

    Return a list of nodes of the longest path in DAG
    """
    path = rustworkx.dag_longest_path(g._graph)
    if not isinstance(g, RetworkXStrDiGraph):
        return path
    return [g._graph.get_node_data(uid).id for uid in path]


def is_weakly_connected(g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge]) -> bool:
    """
    Return True if the graph is weakly connected. Raise NullGraph if an empty graph is passed in
    Args:
        g: The graph to check
    """
    return rustworkx.is_weakly_connected(g._graph)


def weakly_connected_components(
    g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge],
) -> list[set[NodeID]]:
    """
    Return the weakly connected components of the graph

    Args:
        g: The graph to check

    Return a list of lists where each inner list is a weakly connected component
    """
    connected_components = rustworkx.weakly_connected_components(g._graph)
    if not isinstance(g, RetworkXStrDiGraph):
        return connected_components
    return [
        {g._graph.get_node_data(uid).id for uid in comp}
        for comp in connected_components
    ]


def has_cycle(g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge]) -> bool:
    """Test if graph has cycle"""
    return not rustworkx.is_directed_acyclic_graph(g._graph)


def digraph_find_cycle(
    g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge],
    source: NodeID,
) -> list[Edge]:
    """
    Return the first cycle encountered during DFS of a given PyDiGraph from a node, empty list is returned if no cycle is found.

    Args:
        g: The graph to find the cycle in
        source: node id to find a cycle for
    """
    if isinstance(g, RetworkXStrDiGraph):
        source = g.idmap[source]
    cycle = rustworkx.digraph_find_cycle(g._graph, source)
    return [g._graph.get_edge_data(uid, vid) for uid, vid in cycle]


def topological_sort(g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge]) -> list[NodeID]:
    """
    Return a list of node ids in topological sort order. The first node will have no incoming edges and the last node will
    have no outgoing edges if the graph is a DAG. In order words, a node will appear before any nodes it has edges to.

    Args:
        g: The graph to find the topological sort for
    """
    if isinstance(g, RetworkXStrDiGraph):
        return [
            g._graph.get_node_data(uid).id
            for uid in rustworkx.topological_sort(g._graph)
        ]
    return list(rustworkx.topological_sort(g._graph))


def has_path(
    g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge],
    source: NodeID,
    target: NodeID,
    as_undirected: bool = False,
):
    """Checks if a path exists between a source and target node.

    Args:
        g: The graph to check
        source: The source node
        target: The target node
        as_undirected: Whether to treat the graph as undirected
    """
    if isinstance(g, RetworkXStrDiGraph):
        source = g.idmap[source]
        target = g.idmap[target]

    return rustworkx.has_path(g._graph, source, target, as_undirected=as_undirected)
