#! python test_logic_tree.py

from pathlib import Path

import pytest

from nzshm_model.nrml.logic_tree import NrmlDocument

# import nzshm_model
# from nzshm_model.ground_motion_model.logic_tree import (
#     from_xml
# )


"""
>> logic_tree = gmm_tree.xpath('/nrml/logicTree')
>>> len(logic_tree)
0
>>> root = gmm_tree.getroot()
>>> root.xpath('/nrml/logicTree')
[]
>>> root.xpath('//logicTree')
[]
>>> root.xpath('/nrml')
[]
>>> root.xpath('nrml')
[]
>>> namespaces = {'nrml':'http://openquake.org/xmlns/nrml/0.4'}
>>> root.xpath('nrml:nrml', namespaces)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "src/lxml/etree.pyx", line 1591, in lxml.etree._Element.xpath
TypeError: xpath() takes exactly 1 positional argument (2 given)
>>> root.xpath('nrml:nrml', namespaces=namespaces)
[]
>>> root.xpath('/nrml:nrml', namespaces=namespaces)
[<Element {http://openquake.org/xmlns/nrml/0.4}nrml at 0x7f047bea84c0>]
>>> root.xpath('/nrml', namespaces=namespaces)
[]
>>> root.xpath('/nrml:nrml/logicTree', namespaces=namespaces)
[]
>>> root.xpath('/nrml:nrml/nrml:logicTree', namespaces=namespaces)
[<Element {http://openquake.org/xmlns/nrml/0.4}logicTree at 0x7f047bf44080>]
>>> from lxml import objectify
>>> otree = objectify.parse(gmm_lt)
>>> otree

"""

from lxml import objectify

NS = {'nrml': 'http://openquake.org/xmlns/nrml/0.4'}


def from_xml(filepath: Path):
    gmm_tree = objectify.parse(filepath)
    root = gmm_tree.getroot()

    for lt in root.xpath('/nrml:nrml/nrml:logicTree', namespaces=NS):
        yield lt


@pytest.fixture
def gmm_logic_tree_path():
    yield Path(__file__).parent.parent / "GMM_LTs" / "NZ_NSHM_GMM_LT_final_EE.xml"


def test_load_xml(gmm_logic_tree_path):

    """
    <logicTreeBranch branchID="STF22_upper">
                <uncertaintyModel>[Stafford2022]
                  mu_branch = "Upper" </uncertaintyModel>
                <uncertaintyWeight>0.117</uncertaintyWeight>
                    </logicTreeBranch>

    """
    for logic_tree in from_xml(gmm_logic_tree_path):

        # usually we expect just one....
        print(logic_tree, logic_tree.tag)
        print(logic_tree.get('logicTreeID') == 'lt1')

        for ltbs in logic_tree.iterchildren():
            print(ltbs.tag, ltbs.get('uncertaintyType'), ltbs.get('uncertaintyType'))

            assert ltbs.tag == f"{{{NS['nrml']}}}logicTreeBranchSet"

            # assert ltbs.get('uncertaintyType') == "gmpeModel"
            # assert ltbs.get('branchSetID') == "bs_crust"
            # assert ltbs.get('applyToTectonicRegionType') == "Active Shallow Crust"

            for ltb in ltbs.iterchildren():
                print(ltb.tag, ltb.get('branchID'))

                for um in ltb.findall('nrml:uncertaintyModel', namespaces=NS):
                    print(um.text)

                for wm in ltb.findall('nrml:uncertaintyWeight', namespaces=NS):
                    print(wm.text)


def test_build_nrml_tree(gmm_logic_tree_path):

    doc = NrmlDocument.from_xml_file(gmm_logic_tree_path)

    print(doc, doc.logic_trees)

    for logic_tree in doc.logic_trees:
        print(logic_tree.logicTreeID)

        for ltbs in logic_tree.branch_sets:
            print('applyTo', ltbs.applyToTectonicRegionType)
            print('branchSetID', ltbs.branchSetID)

            for branch in ltbs.branches:
                print(branch.uncertainty_models)
                print(branch.uncertainty_weight)

    # assert 0
