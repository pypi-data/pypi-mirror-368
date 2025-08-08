import tempfile, os, shutil
from dataclasses import dataclass
from operator import attrgetter
from textwrap import fill
from typing import Callable, Literal, Optional, Union

import matplotlib.pyplot as plt
import pydot
from graph.interface import Edge, EdgeID, EdgeKey, IGraph, Node, NodeID
from IPython import get_ipython
from IPython.display import display
from PIL import Image


def default_node_styles(node):
    return dict(
        shape="ellipse",
        style="filled",
        color="white",
        fillcolor="lightgray",
    )


def default_edge_styles(edge):
    return dict(color="brown", fontcolor="black")


def draw(
    graph: IGraph[NodeID, EdgeID, EdgeKey, Node, Edge],
    node_label: Callable[[Node], str] = attrgetter("id"),
    node_styles: Callable[[Node], dict] = default_node_styles,
    edge_label: Callable[[Edge], str] = attrgetter("key"),
    edge_styles: Callable[[Edge], dict] = default_edge_styles,
    filename: Optional[str] = None,
    format: Literal["png", "jpg"] = "png",
    quality: int = 100,
    no_display: bool = False,
    line_width: int = 20,
    max_lines: int = 3,
):
    """
    Args:
        graph: the graph to draw
        node_label: the label of a node
        edge_label: the label of an edge
        node_styles: the styles of a node
        edge_styles: the styles of an edge
        filename : str | none
            output to a file or display immediately (inline if this is jupyter lab)
        format: png | jpg
            image format
        quality: int
            if it's < 100, we will compress the image using PIL
        no_display: bool
            if the code is running inside Jupyter, if enable, it returns the object and manually display (default is
            automatically display)
        line_width: int
            every line is at most width characters long
        max_lines: int
            text  will contain at most max_lines lines, with placeholder appearing at the end of the output.
    """
    if filename is None:
        fobj = tempfile.NamedTemporaryFile()
        filename = fobj.name
    else:
        fobj = None

    nodes = graph.nodes()
    idmap = {node.id: i for i, node in enumerate(nodes)}

    dot_g = pydot.Dot(graph_type="digraph")
    for u in nodes:
        label = node_label(u)
        label = fill(label, width=line_width, max_lines=max_lines, placeholder="...")
        dot_g.add_node(
            pydot.Node(name=idmap[u.id], label=norm_value(label), **node_styles(u))
        )

    for e in graph.iter_edges():
        label = edge_label(e)
        label = fill(label, width=line_width, max_lines=max_lines, placeholder="...")

        dot_g.add_edge(
            pydot.Edge(
                idmap[e.source],
                idmap[e.target],
                label=norm_value(label),
                **edge_styles(e),
            )
        )

    # graphviz from anaconda does not support jpeg so use png instead
    dot_g.write(filename, prog="dot", format=format)
    if quality < 100:
        im = Image.open(filename)
        im.save(filename, optimize=True, quality=quality)

    if fobj is not None:
        img = Image.open(filename)
        try:
            if no_display:
                return img
        finally:
            fobj.close()

        try:
            shell = get_ipython().__class__.__name__
            if shell == "ZMQInteractiveShell":
                display(img)
            else:
                plt.imshow(img, interpolation="antialiased")
                plt.show()
        except NameError:
            plt.imshow(img, interpolation="antialiased")
            plt.show()
        finally:
            fobj.close()


DRAW_AUTO_COUNTER = 0


def draw_auto(dirname: str = "/tmp/graphviz", **kwargs):
    """Draw the graph into a directory, naming incrementally for debugging.

    This function is not thread-safe.

    """
    global DRAW_AUTO_COUNTER

    if DRAW_AUTO_COUNTER == 0:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.mkdir(dirname)

    format = kwargs.get("format", "jpg")
    if "filename" in kwargs:
        filename = kwargs.pop("filename")
    else:
        filename = f"g{DRAW_AUTO_COUNTER:03d}.{format}"

    filename = os.path.join(dirname, filename)
    draw(**kwargs, filename=filename)
    DRAW_AUTO_COUNTER += 1


def norm_value(value: Union[int, str]):
    return str(value).replace(":", r"\:")
