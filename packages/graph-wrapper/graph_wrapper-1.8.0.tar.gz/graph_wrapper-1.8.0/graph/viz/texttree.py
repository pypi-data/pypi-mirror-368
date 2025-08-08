from __future__ import annotations

from enum import Enum
from functools import partial
from operator import attrgetter
from typing import Callable, Literal, Optional

from colorama import Back, Fore, Style, init
from graph.interface import BaseEdge, Edge, EdgeID, EdgeKey, IGraph, Node, NodeID


class ColorPalette(Enum):
    LIGHTGREEN = (Back.LIGHTGREEN_EX, "#b7eb8f")
    LIGHTYELLOW = (Back.LIGHTYELLOW_EX, "#ffe58f")
    LIGHTCYAN = (Back.LIGHTCYAN_EX, "#c6e5ff")


def get_edge_sort_key(preferred_keys: set[str], edge: BaseEdge):
    if edge.key in preferred_keys:
        return f"0:{edge.key}"
    return f"1:{edge.key}"


def texttree(
    graph: IGraph[NodeID, EdgeID, EdgeKey, Node, Edge],
    node_label: Callable[[Node], str],
    node_color: Callable[[Node], ColorPalette],
    edge_label: Callable[[Edge], str],
    edge_sort_key: Callable[[Edge], str] = partial(get_edge_sort_key, {"rdfs:label"}),
    colorful: bool = True,
    ignore_isolated_nodes: bool = False,
    env: Literal["terminal", "browser"] = "terminal",
    _cache={},
) -> Optional[str]:
    """Print the graph to the environment if possible. When env is browser, users have to print it manually"""
    if colorful and "init_colorama" not in _cache:
        init()
        _cache["init_colorama"] = True

    def terminal_rnode(node: Node):
        return f"{node_color(node).value[0]}{Fore.BLACK}[{node.id}] {node_label(node)}{Style.RESET_ALL}"

    def browser_rnode(node: Node):
        style = "padding: 2px; border-radius: 3px;"
        return f'<span style="background: {node_color(node).value[1]}; color: black; {style}">[{node.id}] {node_label(node)}</span>'

    def terminal_redge(edge: Edge):
        return f"─[{edge.id}: {Back.LIGHTMAGENTA_EX}{Fore.BLACK}{edge_label(edge)}{Style.RESET_ALL}]→"

    def browser_redge(edge: Edge):
        return f'<span>─[{edge.id}: <span style="text-decoration: underline; background: #ffadd2; color: black">{edge_label(edge)}</span>]→</span>'

    if env == "terminal":
        rnode = terminal_rnode
        redge = terminal_redge
    else:
        rnode = browser_rnode
        redge = browser_redge

    visited = {}
    logs: list[str] = []

    def dfs(start: Node):
        logs.append("\n")
        stack: list[tuple[int, Optional[Edge], Node]] = [(0, None, start)]
        while len(stack) > 0:
            depth, edge, node = stack.pop()
            if edge is None:
                msg = f"{rnode(node)}"
            else:
                msg = f"{redge(edge)} {rnode(node)}"

            if depth > 0:
                indent = "│   " * (depth - 1)
                msg = f"{indent}├── {msg}"

            if node.id in visited:
                msg += f" (visited at {visited[node.id]})"
                logs.append(f"--.\t{msg}\n")
                continue

            counter = len(visited)
            visited[node.id] = counter
            logs.append(f"{counter:02d}.\t{msg}\n")
            outedges = sorted(
                graph.out_edges(node.id),
                key=edge_sort_key,
                reverse=True,
            )
            for edge in outedges:
                target = graph.get_node(edge.target)
                stack.append((depth + 1, edge, target))

    """Print the semantic model, assuming it is a tree"""
    nodes = graph.nodes()
    if ignore_isolated_nodes:
        nodes = [n for n in nodes if graph.degree(n.id) > 0]

    roots = [n for n in nodes if graph.in_degree(n.id) == 0]
    for root in roots:
        dfs(root)

    # doing a final pass to make sure all nodes are printed (including cycles)
    while len(visited) < len(nodes):
        n = [n for n in nodes if n.id not in visited and graph.out_degree(n.id) > 0][0]
        dfs(n)

    if env == "terminal":
        print("".join(logs))
    else:
        return "<pre>" + "".join(logs) + "</pre>"
