import logging
import pathlib
import zipfile
from typing import Any, Dict, Generator, List, Optional, Union

from lxml import etree
from lxml.builder import ElementMaker

from nzshm_model.logic_tree import GMCMBranch, GMCMBranchSet, GMCMLogicTree, SourceLogicTree
from nzshm_model.psha_adapter.openquake.logic_tree import NrmlDocument
from nzshm_model.psha_adapter.psha_adapter_interface import PshaAdapterInterface

try:
    from .toshi import API_KEY, API_URL, SourceSolution
except (ModuleNotFoundError, ImportError):
    print('Running without `toshi` options')

QUICK_TEST = False

log = logging.getLogger(__name__)


def fetch_toshi_source(file_id: str, destination: pathlib.Path) -> pathlib.Path:
    headers = {"x-api-key": API_KEY}
    api = SourceSolution(API_URL, None, None, with_schema_validation=False, headers=headers)
    assert destination.exists()
    file_detail = api.get_source(file_id)
    fname = pathlib.Path(destination) / file_detail['file_name']

    if not fname.exists():
        api.download_file(file_id, destination)
        assert fname.exists()
    else:
        log.info(f'skipping existing: {fname}')
    return fname


def rupt_set_from_meta(meta):
    for itm in meta:
        if itm['k'] == "rupture_set_file_id":
            return itm['v']


def process_gmm_args(args: List[str]) -> Dict[str, Any]:
    def clean_string(string):
        return string.replace('"', '').replace("'", '').strip()

    args_dict = dict()
    for arg in args:
        if '=' in arg:
            k, v = arg.split('=')
            args_dict[clean_string(k)] = clean_string(v)

    return args_dict


class OpenquakeSimplePshaAdapter(PshaAdapterInterface):
    """
    Openquake PSHA simple nrml support.
    """

    def __init__(
        self, source_logic_tree: Optional[SourceLogicTree] = None, gmcm_logic_tree: Optional[GMCMLogicTree] = None
    ):
        self._source_logic_tree = source_logic_tree
        self._gmcm_logic_tree = gmcm_logic_tree
        if source_logic_tree:
            assert source_logic_tree.logic_tree_version == 2

    @staticmethod
    def logic_tree_from_xml(xml_path: Union[pathlib.Path, str]) -> 'GMCMLogicTree':
        """
        Build a GMCMLogicTree from an OpenQuake nrml gmcm logic tree file.
        """
        doc = NrmlDocument.from_xml_file(xml_path)
        if len(doc.logic_trees) != 1:
            raise ValueError("xml must have only 1 logic tree")

        branch_sets = []
        for branch_set in doc.logic_trees[0].branch_sets:
            branches = []
            for branch in branch_set.branches:
                if len(branch.uncertainty_models) != 1:
                    raise ValueError('gmpe branches must have only one uncertainty model')
                gmpe_name = branch.uncertainty_models[0].gmpe_name.replace('[', '').replace(']', '')
                branches.append(
                    GMCMBranch(
                        gsim_name=gmpe_name,
                        gsim_args=process_gmm_args(branch.uncertainty_models[0].arguments),
                        weight=branch.uncertainty_weight,
                    )
                )
            branch_sets.append(
                GMCMBranchSet(
                    tectonic_region_type=branch_set.applyToTectonicRegionType,
                    branches=branches,
                )
            )
        return GMCMLogicTree(
            title=doc.logic_trees[0].logicTreeID,
            branch_sets=branch_sets,
        )

    def build_gmcm_xml(self):
        """Build a gmcm logic tree xml."""
        E = ElementMaker(
            namespace="http://openquake.org/xmlns/nrml/0.5",
            nsmap={"gml": "http://www.opengis.net/gml", None: "http://openquake.org/xmlns/nrml/0.5"},
        )
        NRML = E.nrml
        LT = E.logicTree
        LTBS = E.logicTreeBranchSet
        # LTBL = E.logicTreeBranchingLevel
        LTB = E.logicTreeBranch
        UM = E.uncertaintyModel
        UW = E.uncertaintyWeight

        def um_string(gsim_name, gsim_args):
            return '\n\t\t\t\t'.join(("[" + branch.gsim_name + "]", args2str(branch.gsim_args)))

        def args2str(args):
            string = ''
            for k, v in args.items():
                value = f'"{v}"' if isinstance(v, str) else v
                string += '='.join((k, str(value))) + '\n'
            return string

        i_branch = 0
        lt = LT(logicTreeID="lt1")
        for bs in self.gmcm_logic_tree.branch_sets:
            ltbs = LTBS(
                uncertaintyType="gmpeModel",
                branchSetID="BS:" + bs.tectonic_region_type,
                applyToTectonicRegionType=bs.tectonic_region_type,
            )
            for branch in bs.branches:
                um = um_string(branch.gsim_name, branch.gsim_args)
                ltb = LTB(UM(um), UW(str(branch.weight)), branchID=branch.gsim_name + str(i_branch))
                ltbs.append(ltb)
                i_branch += 1
            lt.append(ltbs)
        nrml = NRML(lt)
        return etree.tostring(nrml, pretty_print=True).decode()

    def build_sources_xml(self, source_map):
        """Build a source model for a set of LTBs with their source files."""
        E = ElementMaker(
            namespace="http://openquake.org/xmlns/nrml/0.5",
            nsmap={"gml": "http://www.opengis.net/gml", None: "http://openquake.org/xmlns/nrml/0.5"},
        )
        NRML = E.nrml
        LT = E.logicTree
        LTBS = E.logicTreeBranchSet
        LTBL = E.logicTreeBranchingLevel
        LTB = E.logicTreeBranch
        UM = E.uncertaintyModel
        UW = E.uncertaintyWeight

        """
        # Build from existing NRML logic_tree
        nrml_logic_tree = self.config()
        # print(nrml_logic_tree)
        ltbl = LTBL(branchingLevelID="1")
        for branch_set in nrml_logic_tree.branch_sets:
            ltbs = LTBS(uncertaintyType="sourceModel", branchSetID=branch_set.branchSetID)
            for branch in branch_set.branches:
                ltb = LTB(UW(str(branch.uncertainty_weight)), branchID=branch.branchID)
                for um in branch.uncertainty_models:
                    files = "\n"
                    for filepath in source_map.get(um.toshi_nrml_id, []):
                        files += f"\t\"{filepath}\"\n"
                    ltb.append(UM(files))
                ltbs.append(ltb)
            ltbl.append(ltbs)
        """

        # Build from the source_logic_tree
        ltbl = LTBL(branchingLevelID="1")
        for fs in self.source_logic_tree.branch_sets:
            ltbs = LTBS(uncertaintyType="sourceModel", branchSetID=fs.short_name)
            for branch in fs.branches:
                branch_name = str(branch.values)
                files = ""
                ltv = getattr(self.source_logic_tree, "logic_tree_version", 0)
                if ltv >= 2:
                    # new logic trees
                    for source in branch.sources:
                        for filepath in source_map.get(source.nrml_id):
                            if not filepath.suffix == '.xml':
                                continue
                            files += f"\t{filepath}\n"
                        ltb = LTB(UM(files), UW(str(branch.weight)), branchID=branch_name)
                # else:
                #     # old style logic tree
                #     if source_map.get(branch.onfault_nrml_id):
                #         for filepath in source_map.get(branch.onfault_nrml_id):
                #             if not filepath.suffix == '.xml':
                #                 continue
                #             files += f"\t'{filepath}'\n"
                #     if source_map.get(branch.distributed_nrml_id):
                #         for filepath in source_map.get(branch.distributed_nrml_id):
                #             files += f"\t'{filepath}'\n"
                #     ltb = LTB(UM(files), UW(str(branch.weight)), branchID=str(branch.values))
                ltbs.append(ltb)
            ltbl.append(ltbs)
        nrml = NRML(LT(ltbl, logicTreeID="Combined"))
        return etree.tostring(nrml, pretty_print=True).decode()

    def write_config(
        self,
        cache_folder: Union[pathlib.Path, str],
        target_folder: Union[pathlib.Path, str],
        source_map: Union[None, Dict[str, list[pathlib.Path]]] = None,
    ) -> pathlib.Path:
        destination = pathlib.Path(target_folder)
        assert destination.exists()
        assert destination.is_dir()

        source_map = source_map or self.unpack_resources(cache_folder, target_folder)
        xmlstr = self.build_sources_xml(source_map)

        target_file = pathlib.Path(destination, 'sources.xml')
        with open(target_file, 'w') as fout:
            fout.write(xmlstr)
        return target_file

    def unpack_resources(
        self, cache_folder: Union[pathlib.Path, str], target_folder: Union[pathlib.Path, str]
    ) -> Dict[str, list[pathlib.Path]]:
        target = pathlib.Path(target_folder)
        target.mkdir(parents=True, exist_ok=True)
        source_map = {}
        limit = 2
        count = 0
        for file_id, filepath, uncertainty_model in self.fetch_resources(cache_folder):
            count += 1
            destination = target / uncertainty_model.path().parent
            destination.mkdir(parents=True, exist_ok=True)
            zf = zipfile.ZipFile(filepath)
            source_paths = []
            for name in zf.namelist():
                if not pathlib.Path(destination, name).exists():
                    zf.extract(name, destination)
                else:
                    log.info(f"skip existing {name}")
                source_paths.append(pathlib.Path(destination, name).relative_to(target))
            source_map[uncertainty_model.toshi_nrml_id] = source_paths
            if count >= limit and QUICK_TEST:
                break

        return source_map
        # # rename the extracted files
        # for name in zf.namelist():
        #     # rename
        #     extracted = pathlib.Path(destination, name)
        #     assert extracted.exists()
        #     if file_prefix:
        #         prefixed = pathlib.Path(destination, f"{file_prefix}_{name}")
        #         extracted.rename(prefixed)

    def fetch_resources(
        self, cache_folder: Union[pathlib.Path, str]
    ) -> Generator[tuple[Any, pathlib.Path, Any], None, None]:
        destination = pathlib.Path(cache_folder)
        destination.mkdir(parents=True, exist_ok=True)
        nrml_logic_tree = self.config()
        for branch_set in nrml_logic_tree.branch_sets:
            for branch in branch_set.branches:
                for um in branch.uncertainty_models:
                    filepath = fetch_toshi_source(um.toshi_nrml_id, destination)
                    yield um.toshi_nrml_id, filepath, um

    def config(self):
        return NrmlDocument.from_model_slt(self._source_logic_tree).logic_trees[0]

    @property
    def source_logic_tree(self):
        return self._source_logic_tree

    @property
    def gmcm_logic_tree(self):
        return self._gmcm_logic_tree
