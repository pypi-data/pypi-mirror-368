import os
import shutil
import logging
from dataclasses import dataclass
from typing import Callable
from pathlib import Path

import graphviz


logger = logging.getLogger(__name__)


@dataclass
class TreeFunctions:
    find_children: Callable[[], list]
    find_decision_content: Callable[[], str]
    find_leaf_content: Callable[[], str]


def _sub_string(node, tree_functions, spacing="  "):
    """Visualize a tree in string form"""
    out_str = ""
    children = tree_functions.find_children(node)
    if children is None or len(children) == 0:
        out_str = f"{tree_functions.find_leaf_content(node)}\n"
    else:
        out_str = f"{tree_functions.find_decision_content(node)},\n"
        for i, child in enumerate(children):
            out_str = (
                f"{out_str}"
                f"\n{spacing}Child {i}:"
                f"{_sub_string(child, tree_functions, 2 * spacing)}"
            )
    return out_str


def _sub_graph(
    graph,
    node,
    tree_functions,
    label="0",
    parent_label=None,
):
    children = tree_functions.find_children(node)
    if children is None or len(children) == 0:
        graph.node(label, tree_functions.find_leaf_content(node), shape="ellipse")
    else:
        graph.node(label, tree_functions.find_decision_content(node), shape="box")
        for i, child in enumerate(children):
            _sub_graph(
                graph,
                child,
                tree_functions,
                f"{label}|{i}",
                parent_label=label,
            )
    if parent_label:
        graph.edge(parent_label, label)


def has_graphviz():
    graphviz_path = shutil.which("dot")
    return graphviz_path and os.access(graphviz_path, os.X_OK)


def display_tree(
    root,
    path: Path,
    find_children: Callable[[], list],
    find_decision_content: Callable[[], str],
    find_leaf_content: Callable[[], str],
):
    """
    Allows classes which have attributes that are instances of the same class (children)
    to be visualised as a decision tree.
    Uses graphviz by default, alternatively, if system-wide graphviz is not available,
    uses a string representation .

    :param callable find_children: Function that takes a "node" and returns a list of
        children nodes
    :param callable find_decision_content: Function that takes a "node" and returns a
        string for content for decision nodes
    :param callable find_leaf_content: Function that takes a "node" and returns a
        string for content for leaf nodes
    """
    tree_functions = TreeFunctions(
        find_children, find_decision_content, find_leaf_content
    )
    if has_graphviz():
        graph = graphviz.Digraph(path.name, comment="Graphviz representation of tree")
        graph.format = "svg"
        _sub_graph(graph, root, tree_functions)
        graph.render(directory=path.parent, filename=path.name, cleanup=True).replace(
            "\\", "/"
        )
    else:
        # If system graphviz install isn't available, use string representation
        logger.info(
            "Warning: System graphviz install could not be found, creating string "
            "representation instead"
        )
        with open(f"{path}.txt", "w", encoding="utf-8") as f:
            f.write(_sub_string(root, tree_functions))
