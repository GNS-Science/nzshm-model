import pathlib
import zipfile
from typing import Union

from lxml import etree
from lxml.builder import ElementMaker

from nzshm_model.psha_adapter.openquake.logic_tree import NrmlDocument
from nzshm_model.psha_adapter.psha_adapter_interface import PshaAdapterInterface

try:
    from .toshi import API_KEY, API_URL, SourceSolution
except (ModuleNotFoundError, ImportError):
    print('Running without `toshi` options')


def build_sources_xml(
    source_logic_tree,
):
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

    for fs in source_logic_tree.fault_systems:
        ltbs = LTBS(uncertaintyType="sourceModel", branchSetID=fs.short_name)
        for branch in fs.branches:
            branch_name = str(branch.values)
            files = ""
            for source in branch.sources:
                files += f"\t{source.nrml_id}\t"  # this should be the unpacked file sources!
            ltb = LTB(UM(files), UW(str(branch.weight)), branchID=branch_name)
            ltbs.append(ltb)

    nrml = NRML(LT(LTBL(ltbs, branchingLevelID="1"), logicTreeID="Combined"))
    return etree.tostring(nrml, pretty_print=True).decode()


class OpenquakeSimplePshaAdapter(PshaAdapterInterface):
    """
    Openquake PSHA simple nrml support.
    """

    @staticmethod
    def _get_destination_args(uncertainty_model, target_folder: Union[pathlib.Path, str], long_filenames: bool):

        if long_filenames:
            # flatten the paths
            file_prefix = str(uncertainty_model.path().parent).replace('/', "_")
            destination = pathlib.Path(target_folder)  # / current_model.version
            return dict(file_prefix=file_prefix, destination=destination)
        else:
            # otherwise use folders
            destination = pathlib.Path(target_folder) / uncertainty_model.path.parent
            return dict(destination=destination)

    def write_config(self, target_folder: Union[pathlib.Path, str], long_filenames: bool = False):  # -> pathlib.Path
        destination = pathlib.Path(target_folder)
        assert destination.exists()
        assert destination.is_dir()

        ## TODO implement XML writer
        assert self._source_logic_tree.logic_tree_version >= 2

        for fs in self._source_logic_tree.fault_systems:
            # click.echo(f"branch set {branch_set.branchSetID}")
            for branch in fs.branches:
                # click.echo(f"branch: {branch.branchID}")
                for source in branch.sources:
                    path = pathlib.Path(self._source_logic_tree.version, fs.short_name, branch.tag())
                    source.path = path
                    kwargs = self._get_destination_args(source, target_folder, long_filenames=False)
                    print(kwargs)

                    # TODO: yield list of sources ... either from filesystem == fragile, or

        # assert 0
        xmlstr = build_sources_xml(self._source_logic_tree)

        print(xmlstr)

        # assert 0
        # target_file = pathlib.Path(destination, 'sources.xml')
        # with open(target_file, 'w') as fout:
        #     fout.write(self.config())
        # return target_file

    def fetch_resources(self, target_folder, long_filenames=False):
        # raise NotImplementedError()
        # return super().fetch_resources(target_folder)
        nrml_logic_tree = self.config()
        # self._source_nrml_logic_tree
        for branch_set in nrml_logic_tree.branch_sets:
            # click.echo(f"branch set {branch_set.branchSetID}")
            for branch in branch_set.branches:
                # click.echo(f"branch: {branch.branchID}")
                for um in branch.uncertainty_models:
                    kwargs = self._get_destination_args(um, target_folder, long_filenames)
                    fetch_toshi_source(file_id=um.path().name, **kwargs)

    def config(self):
        return NrmlDocument.from_model_slt(self._source_logic_tree).logic_trees[0]


def rupt_set_from_meta(meta):
    for itm in meta:
        if itm['k'] == "rupture_set_file_id":
            return itm['v']


def fetch_toshi_source(destination, file_id, file_prefix=""):
    headers = {"x-api-key": API_KEY}
    api = SourceSolution(API_URL, None, None, with_schema_validation=False, headers=headers)

    # click.echo(f'checking {file_id}')
    file_detail = api.get_source(file_id)
    # click.echo(file_detail)

    destination.mkdir(parents=True, exist_ok=True)

    fname = pathlib.Path(destination) / file_detail['file_name']
    # if not fname.exists():
    # click.echo(f'fetching {fname}')
    api.download_file(file_id, destination)

    ## unpack zipfiles
    # click.echo(file_detail.get('__typename'))

    zf = zipfile.ZipFile(fname)
    # click.echo(zf.namelist())
    for name in zf.namelist():
        zf.extract(name, destination)

    # rename the extracted files
    for name in zf.namelist():
        # rename
        extracted = pathlib.Path(destination, name)
        assert extracted.exists()
        if file_prefix:
            prefixed = pathlib.Path(destination, f"{file_prefix}_{name}")
            extracted.rename(prefixed)

    # delete the zipfiles
    fname.unlink()
