from pathlib import Path
import os
import shutil

from iccore.test_utils import get_test_output_dir

from icplot.tree import display_tree


class BinaryTreeNode:
    def __init__(self, int_1: int, int_2: int, left=None, right=None):
        self.int_1 = int_1
        self.int_2 = int_2
        self.left = left
        self.right = right


def test_binary_tree():
    def find_decision_content(node: BinaryTreeNode):
        return f"This is a decision node, values are {node.int_1}, {node.int_2}"

    def find_leaf_content(node: BinaryTreeNode):
        return f"This is a leaf node values are {node.int_1}, {node.int_2}"

    def find_children(node: BinaryTreeNode):
        return [i for i in [node.left, node.right] if i is not None]

    root = BinaryTreeNode(
        0,
        1,
        BinaryTreeNode(2, 3, BinaryTreeNode(6, 7), BinaryTreeNode(8, 9)),
        BinaryTreeNode(4, 5),
    )

    output_dir = get_test_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    display_tree(
        root,
        output_dir / "tree",
        find_children,
        find_decision_content,
        find_leaf_content,
    )
    assert (
        Path(output_dir / "tree.svg").exists() or Path(output_dir / "tree.txt").exists()
    )
    shutil.rmtree(output_dir)


class TreeNode:
    def __init__(self, int_1: int, int_2: int, children=None):
        self.int_1 = int_1
        self.int_2 = int_2
        self.children = children


def test_tree():
    def find_content(node: TreeNode):
        return f"This node's values are {node.int_1}, {node.int_2}"

    def find_children(node: TreeNode):
        return node.children

    root = TreeNode(
        0,
        1,
        [
            TreeNode(
                2,
                3,
                [TreeNode(6, 7), TreeNode(8, 9), TreeNode(10, 11), TreeNode(12, 13)],
            ),
            TreeNode(4, 5),
        ],
    )

    output_dir = get_test_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    display_tree(root, output_dir / "tree", find_children, find_content, find_content)
    assert (
        Path(output_dir / "tree.svg").exists() or Path(output_dir / "tree.txt").exists()
    )
    shutil.rmtree(output_dir)
