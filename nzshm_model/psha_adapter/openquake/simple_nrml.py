import csv
import logging
import pathlib
import warnings
import zipfile
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Union

from lxml import etree
from lxml.builder import ElementMaker

from nzshm_model.logic_tree import GMCMBranch, GMCMBranchSet, GMCMLogicTree
from nzshm_model.psha_adapter import (
    ConfigPshaAdapterInterface,
    GMCMPshaAdapterInterface,
    ModelPshaAdapterInterface,
    SourcePshaAdapterInterface,
)
from nzshm_model.psha_adapter.openquake.logic_tree import NrmlDocument

if TYPE_CHECKING:
    from nzshm_model import NshmModel
    from nzshm_model.logic_tree import SourceLogicTree
    from nzshm_model.psha_adapter.openquake.logic_tree import LogicTree

    from .hazard_config import OpenquakeConfig

try:
    from .toshi import API_KEY, API_URL, SourceSolution
except (ModuleNotFoundError, ImportError):
    print('Running without `toshi` options')


QUICK_TEST = False

log = logging.getLogger(__name__)


def make_target(target_folder) -> pathlib.Path:
    destination = pathlib.Path(target_folder)
    destination.mkdir(parents=True, exist_ok=True)
    return destination


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


def process_gmm_args(args: List[str]) -> Dict[str, Any]:
    def clean_string(string):
        return string.replace('"', '').replace("'", '').strip()

    args_dict = dict()
    for arg in args:
        if '=' in arg:
            k, v = arg.split('=')
            args_dict[clean_string(k)] = clean_string(v)

    return args_dict


def gmcm_branch_from_element_text(element_text: str) -> GMCMBranch:
    """Produce a GMCMBranch from NRML Uncertainty node text"""
    lines = element_text.split("\n")
    gmpe_name = lines[0].strip().replace('[', '').replace(']', '')
    arguments = [arg.strip() for arg in lines[1:]]

    return GMCMBranch(gsim_name=gmpe_name, gsim_args=process_gmm_args(arguments), weight=0.0)


class OpenquakeGMCMPshaAdapter(GMCMPshaAdapterInterface):
    """
    Openquake GMCMLogicTree apapter
    """

    def __init__(self, target: GMCMLogicTree):
        self.gmcm_logic_tree = target

    def write_config(self, target_folder: Union[pathlib.Path, str]) -> pathlib.Path:

        target_folder = make_target(target_folder)

        gmcm_xmlstr = self.build_gmcm_xml()
        gmcm_file = target_folder / 'gsim_model.xml'
        with gmcm_file.open('w') as fout:
            fout.write(gmcm_xmlstr)

        return gmcm_file

    @staticmethod
    def gmcm_logic_tree_from_xml(xml_path: Union[pathlib.Path, str]) -> GMCMLogicTree:
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
                        tectonic_region_type=branch_set.applyToTectonicRegionType,
                    )
                )
            branch_sets.append(
                GMCMBranchSet(
                    branches=branches,
                )
            )
        return GMCMLogicTree(
            title=doc.logic_trees[0].logicTreeID,
            branch_sets=branch_sets,
        )

    def build_gmcm_xml(self) -> str:
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


class OpenquakeSourcePshaAdapter(SourcePshaAdapterInterface):
    """
    Openquake SourceLogicTree adapter
    """

    def __init__(self, target: 'SourceLogicTree'):
        self.source_logic_tree = target

    def write_config(
        self,
        cache_folder: Union[pathlib.Path, str],
        target_folder: Union[pathlib.Path, str],
        source_map: Union[None, Dict[str, list[pathlib.Path]]] = None,
    ) -> pathlib.Path:

        target_folder = make_target(target_folder)

        sources_folder = target_folder / 'sources'
        sources_folder.mkdir(exist_ok=True)
        source_map = source_map or self.unpack_resources(cache_folder, sources_folder)
        source_xmlstr = self.build_sources_xml(source_map)
        sources_file = sources_folder / 'sources.xml'
        with sources_file.open('w') as fout:
            fout.write(source_xmlstr)

        return sources_file

    def build_sources_xml(self, source_map) -> str:
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
        nrml_logic_tree = self.sources_document()
        for branch_set in nrml_logic_tree.branch_sets:
            for branch in branch_set.branches:
                for um in branch.uncertainty_models:
                    filepath = fetch_toshi_source(um.toshi_nrml_id, destination)
                    yield um.toshi_nrml_id, filepath, um

    def sources_document(self) -> 'LogicTree':
        return NrmlDocument.from_model_slt(self.source_logic_tree).logic_trees[0]


class OpenquakeConfigPshaAdapter(ConfigPshaAdapterInterface):
    def __init__(self, target: 'OpenquakeConfig'):
        self.hazard_config = target
        self._sources_file: Optional[pathlib.Path] = None
        self._gmcm_file: Optional[pathlib.Path] = None
        self._site_file: Optional[pathlib.Path] = None

    def set_source_file(self, sources_file: Union[pathlib.Path, str]):
        self._sources_file = pathlib.Path(sources_file)

    def set_gmcm_file(self, gmcm_file: Union[pathlib.Path, str]):
        self._gmcm_file = pathlib.Path(gmcm_file)

    def write_site_file(self, site_file: Union[pathlib.Path, str]):
        """
        writes the OpenQuake site_model_file

        Arguments:
            site_file: path to the site_model_file
        """

        site_file = pathlib.Path(site_file)
        locations = self.hazard_config.locations
        site_params = self.hazard_config.site_parameters

        if not locations:
            raise Exception("locations not yet set in configuration")

        with site_file.open('w') as fout:
            site_writer = csv.writer(fout, lineterminator='\n')
            header = ['lon', 'lat']
            if site_params:
                header += list(site_params.keys())
            site_writer.writerow(header)

            sites: Dict[str, tuple] = {
                'lon': tuple(loc.lon for loc in locations),
                'lat': tuple(loc.lat for loc in locations),
            }
            if self.hazard_config.site_parameters:
                sites.update(self.hazard_config.site_parameters)
            rows = [[param[i] for param in sites.values()] for i in range(len(locations))]
            site_writer.writerows(rows)

        self._site_file = site_file

    def write_config(self, target_folder: Union[pathlib.Path, str]) -> pathlib.Path:

        target_folder = make_target(target_folder)

        if self.hazard_config.locations:
            site_file = target_folder / 'sites.csv'
            self.write_site_file(site_file)
            self.hazard_config.set_site_filepath(site_file.relative_to(target_folder))
        else:
            site_file = target_folder / '<path to site file>'

        # check that required settings not included in default exist
        if not self.hazard_config.is_complete():
            warnings.warn("hazard configuration is not complete; cannot be used to run OpenQuake job")

        sources_file = target_folder / '<path to source file>' if not self._sources_file else self._sources_file
        gmcm_file = target_folder / '<path to gmcm file>' if not self._gmcm_file else self._gmcm_file
        self.hazard_config.set_source_logic_tree_file(sources_file.relative_to(target_folder))
        self.hazard_config.set_gsim_logic_tree_file(gmcm_file.relative_to(target_folder))
        job_file = target_folder / 'job.ini'
        with job_file.open('w') as fout:
            self.hazard_config.write(fout)

        return job_file


class OpenquakeModelPshaAdapter(ModelPshaAdapterInterface):
    """
    Openquake PSHA adapter.
    """

    def __init__(self, target: 'NshmModel'):
        self.model = target
        self.source_adapter = self.model.source_logic_tree.psha_adapter(OpenquakeSourcePshaAdapter)
        self.gmcm_adapter = self.model.gmm_logic_tree.psha_adapter(OpenquakeGMCMPshaAdapter)
        self.config_adapter = self.model.hazard_config.psha_adapter(OpenquakeConfigPshaAdapter)

    def write_config(
        self,
        cache_folder: Union[pathlib.Path, str],
        target_folder: Union[pathlib.Path, str],
        source_map: Optional[Dict[str, list[pathlib.Path]]] = None,
    ) -> pathlib.Path:

        target_folder = make_target(target_folder)

        source_file = self.source_adapter.write_config(cache_folder, target_folder, source_map)
        gmcm_file = self.gmcm_adapter.write_config(target_folder)

        self.config_adapter.set_source_file(source_file)  # type: ignore
        self.config_adapter.set_gmcm_file(gmcm_file)  # type: ignore

        job_file = self.config_adapter.write_config(target_folder)

        return job_file
