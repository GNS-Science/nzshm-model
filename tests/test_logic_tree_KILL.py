#! python test_logic_tree.py

from nzshm_model.source_logic_tree.logic_tree_KILL import Branch, BranchLevel, FaultSystemLogicTree


class TestBranchLevel:
    def test_init(self):
        bl = BranchLevel(name='C', long_name='area-magnitude scaling')
        print(bl)
        assert bl.name == 'C'
        assert bl.long_name == 'area-magnitude scaling'

    def test_connected(self):
        bl = BranchLevel('C', 'area-magnitude scaling')
        b = Branch(value=4.0)

        b.branch_level = bl
        bl.branches.append(b)

        assert b.value == 4.0
        assert b in bl.branches
        assert b.branch_level.name == "C"

    def test_connected_better(self):
        bl = BranchLevel('C', 'longy')
        b = Branch(value=True, branch_level=bl)
        assert b in bl.branches
        assert b.branch_level.name == "C"


class TestBranch:
    def test_boolean_value(self):
        b = Branch(value=True)
        print(b)
        assert b.value is True

    def test_float_value(self):
        b = Branch(value=1.0)
        print(b)
        assert b.value == 1.0

    def test_int_value(self):
        b = Branch(value=1)
        print(b)
        assert b.value == 1

    def test_str_value(self):
        b = Branch(value="1")
        print(b)
        assert b.value == "1"

    def test_unconnected(self):
        b = Branch("ABC")
        assert b.value == "ABC"


class TestFaultSystemLogicTree:
    def test_init(self):

        tree = FaultSystemLogicTree("Hik", "Hikurangi")
        assert tree.short_name == "Hik"
        assert tree.long_name == "Hikurangi"
        assert tree.name == "Hik"
        assert tree.inversion_source == ""
        assert tree.distributed_source == ""

    def test_connected(self):
        bl = BranchLevel('C', 'area-magnitude scaling')
        # b = Branch(value=4, branch_level=bl)
        tree = FaultSystemLogicTree("Hik", "Hikurangi")
        tree.branch_levels.append(bl)
        assert tree.name == "Hik, C"

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
