#! python test_logic_tree.py

from nzshm_model.source_logic_tree.logic_tree import Branch, BranchLevel  # , LogicTreeLeaf


class TestBranchLevel:
    def test_a(self):
        bl = BranchLevel('shorty', 'longy')
        print(bl)
        assert bl.name == 'shorty'
        assert bl.long_name == 'longy'

    def test_connected(self):
        bl = BranchLevel('shorty', 'longy')
        b = Branch(value=True, weight=1.0)

        b.branch_level = bl
        bl.branches.append(b)

        assert b.weight == 1.0
        assert b.value is True
        assert b in bl.branches
        assert b.branch_level.name == "shorty"

    def test_connected_better(self):
        bl = BranchLevel('shorty', 'longy')
        b = Branch(value=True, weight=1.0, branch_level=bl)
        assert b in bl.branches
        assert b.branch_level.name == "shorty"


class TestBranch:
    def test_boolean_value(self):
        b = Branch(value=True, weight=1.0)
        print(b)
        assert b.weight == 1.0
        assert b.value is True

    def test_float_value(self):
        b = Branch(value=1.0, weight=1.0)
        print(b)
        assert b.weight == 1.0
        assert b.value == 1.0

    def test_int_value(self):
        b = Branch(value=1, weight=1.0)
        print(b)
        assert b.weight == 1.0
        assert b.value == 1

    def test_str_value(self):
        b = Branch(value="1", weight=1.0)
        print(b)
        assert b.weight == 1.0
        assert b.value == "1"

    def test_unconnected(self):
        b = Branch("ABC", 2.0)
        assert b.value == "ABC"
        assert b.branch_level is None


# class TestLeaf:
#     def test_init(self):

#         leaf = LogicTreeLeaf(inversion_source="X")
#         assert leaf.name == ""
#         assert leaf.inversion_source == "X"
#         assert leaf.distributed_source == ""

#     def test_connected(self):
#         bl = BranchLevel('shorty', 'longy')
#         b = Branch(value=True, weight=1.0, branch_level=bl)
#         leaf = LogicTreeLeaf(branch=b, inversion_source="X")

#         # b.branch_level = bl
#         # bl.branches.append(b)
#         # leaf.branch = b
#         # leaf.inversion_source = "X"
#         leaf.distributed_source = "Y"

#         assert b.weight == 1.0
#         assert b.value is True
#         assert b in bl.branches
#         assert b.branch_level.name == "shorty"
#         assert leaf.branch.branch_level.name == 'shorty'
#         assert leaf.name == "shorty"
#         assert leaf.inversion_source == "X"
