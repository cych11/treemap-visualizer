"""
Assignment 2 - Sample Tests

=== CSC148 Winter 2024 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2024 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains sample tests for Assignment 2, Tasks 1 and 2.
The tests use the provided example-directory, so make sure you have downloaded
and extracted it into the same place as this test file.
This test suite is very small. You should plan to add to it significantly to
thoroughly test your code.

IMPORTANT NOTES:
    - If using PyCharm, go into your Settings window, and go to
      Editor -> General.
      Make sure the "Ensure line feed at file end on Save" is NOT checked.
      Then, make sure none of the example files have a blank line at the end.
      (If they do, the data size will be off.)

    - os.listdir behaves differently on different
      operating systems.  These tests expect the outcomes that one gets
      when running on the *Teaching Lab machines*.
      Please run all of your tests there - otherwise,
      you might get inaccurate test failures!

    - Depending on your operating system or other system settings, you
      may end up with other files in your example-directory that will cause
      inaccurate test failures. That will not happen on the Teachin Lab
      machines.  This is a second reason why you should run this test module
      there.
"""
import math
import os

from hypothesis import given
from hypothesis.strategies import integers

from tm_trees import TMTree, FileSystemTree

# This should be the path to the "workshop" folder in the sample data.
# You may need to modify this, depending on where you downloaded and
# extracted the files.
EXAMPLE_PATH = os.path.join(os.getcwd(), 'example-directory', 'workshop')


def test_single_file() -> None:
    """Test a tree with a single file.
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    assert tree._name == 'draft.pptx'
    assert tree._subtrees == []
    assert tree._parent_tree is None
    assert tree.data_size == 58
    assert is_valid_colour(tree._colour)


def test_single_folder() -> None:
    """Test a tree with a single folder!!!
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'prep'))
    assert tree._name == 'prep'
    assert len(tree._subtrees) == 2
    assert tree._parent_tree is None
    assert tree.data_size == 22
    assert is_valid_colour(tree._colour)


def test_example_data() -> None:
    """Test the root of the tree at the 'workshop' folder in the example data
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    assert tree._name == 'workshop'
    assert tree._parent_tree is None
    assert tree.data_size == 151
    assert is_valid_colour(tree._colour)

    assert len(tree._subtrees) == 3
    for subtree in tree._subtrees:
        # Note the use of is rather than ==.
        # This checks ids rather than values.
        assert subtree._parent_tree is tree


@given(integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000))
def test_single_file_rectangles(x, y, width, height) -> None:
    """Test that the correct rectangle is produced for a single file."""
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    tree.update_rectangles((x, y, width, height))
    rects = tree.get_rectangles()

    # This should be just a single rectangle and colour returned.
    assert len(rects) == 1
    rect, colour = rects[0]
    assert rect == (x, y, width, height)
    assert is_valid_colour(colour)


def test_example_data_rectangles() -> None:
    """This test sorts the subtrees, because different operating systems have
    different behaviours with os.listdir.

    You should *NOT* do any sorting in your own code
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)

    tree.expand_all()
    tree.update_rectangles((0, 0, 200, 100))
    rects = tree.get_rectangles()

    # IMPORTANT: This test should pass when you have completed Task 2, but
    # will fail once you have completed Task 5.
    # You should edit it as you make progress through the tasks,
    # and add further tests for the later task functionality.
    assert len(rects) == 6

    # UPDATED:
    # Here, we illustrate the correct order of the returned rectangles.
    # Note that this corresponds to the folder contents always being
    # sorted in alphabetical order. This is enforced in these sample tests
    # only so that you can run them on your own computer, rather than on
    # the Teaching Labs.
    actual_rects = [r[0] for r in rects]
    expected_rects = [(0, 0, 94, 2), (0, 2, 94, 28), (0, 30, 94, 70),
                      (94, 0, 76, 100), (170, 0, 30, 72), (170, 72, 30, 28)]

    assert len(actual_rects) == len(expected_rects)
    for i in range(len(actual_rects)):
        assert expected_rects[i] == actual_rects[i]


def test_change_size_minimum() -> None:
    """
    Test that the change_size function cannot make a file have a size lower than
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    tree.change_size(-0.99)
    print(tree.data_size)
    assert tree.data_size == 1


@given(integers(min_value=-1000, max_value=1000))
def test_change_size(factor) -> None:
    factor /= 100000
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'activities', 'images'))
    for x in tree._subtrees:
        if not x._subtrees:
            old_size = x.data_size
            x.change_size(factor)
            assert (x.data_size ==
                    math.ceil(old_size * factor) + old_size) \
                if factor >= 0 \
                else old_size - math.ceil(old_size * -factor)


def test_valid_move() -> None:
    """
    test that a leaf can move into a non-empty folder
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH))
    leaf = None
    destination = None
    for subtree in tree._subtrees:
        if subtree._name == 'draft.pptx':
            leaf = subtree
        elif subtree._name == 'prep':
            destination = subtree
    leaf.move(destination)
    assert destination._subtrees[-1] == leaf


def test_invalid_move_leaf_to_leaf() -> None:
    """
    test that a leaf cannot be moved into a leaf
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH))
    leaf = None
    destination = None
    for subtree in tree._subtrees:
        if subtree._name == 'activities':
            for subtree2 in subtree._subtrees:
                if subtree2._name == 'images':
                    for subtree3 in subtree2._subtrees:
                        if subtree3._name == 'Q3.pdf':
                            leaf = subtree3
                        elif subtree3._name == 'Q2.pdf':
                            destination = subtree3
    assert leaf._subtrees == [] and destination._subtrees == []


def test_invalid_move_folder_to_leaf() -> None:
    """
    test that a folder cannot move into a leaf
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH))
    leaf = None
    destination = None
    for subtree in tree._subtrees:
        if subtree._name == 'draft.pptx':
            destination = subtree
        elif subtree._name == 'prep':
            leaf = subtree
    leaf.move(destination)
    assert leaf not in destination._subtrees and destination._subtrees == []


def test_invalid_move_leaf_to_empty_folder() -> None:
    """
    test that a leaf cannot be moved into an empty folder (considered a leaf)
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH))
    leaf = None
    destination = None
    leaf_pt = None
    for subtree in tree._subtrees:
        if subtree._name == 'prep':
            for subtree2 in subtree._subtrees:
                if subtree2._name == 'images':
                    destination = subtree2
                    subtree2._subtrees[0].delete_self()
                    leaf = subtree._subtrees[0]
                    leaf_pt = leaf._parent_tree
    leaf.move(destination)
    assert leaf not in destination._subtrees and leaf._parent_tree == leaf_pt


def test_delete_self() -> None:
    """
    Test the delete_self() function
    """
    tree = False
    tree_parent = None
    destination = FileSystemTree(EXAMPLE_PATH)
    for subtree1 in destination._subtrees:
        if subtree1._name == 'activities':
            for subtree2 in subtree1._subtrees:
                if subtree2._name == 'Plan.tex':
                    tree = subtree2
                    tree_parent = subtree1

    tree.delete_self()
    assert tree._parent_tree is tree_parent
    assert tree not in tree_parent._subtrees


##############################################################################
# Helpers
##############################################################################


def is_valid_colour(colour: tuple[int, int, int]) -> bool:
    """Return True iff <colour> is a valid colour. That is, if all of its
    values are between 0 and 255, inclusive.
    """
    for i in range(3):
        if not 0 <= colour[i] <= 255:
            return False
    return True


def _sort_subtrees(tree: TMTree) -> None:
    """Sort the subtrees of <tree> in alphabetical order.
    THIS IS FOR THE PURPOSES OF THE SAMPLE TEST ONLY; YOU SHOULD NOT SORT
    YOUR SUBTREES IN THIS WAY. This allows the sample test to run on different
    operating systems.

    This is recursive, and affects all levels of the tree.
    """
    if not tree.is_empty():
        for subtree in tree._subtrees:
            _sort_subtrees(subtree)

        tree._subtrees.sort(key=lambda t: t._name)


if __name__ == '__main__':
    import pytest

    pytest.main(['a2_my_tests.py'])
