#! logic_tree.py

"""
Define source logic tree structures used in NSHM.
"""
import os
import pathlib
import zipfile
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from functools import reduce
from itertools import product
from math import isclose
from operator import add, mul
from typing import Any, Dict, Generator, Iterable, List, Type, Union

from nshm_toshi_client.toshi_file import ToshiFile

from nzshm_model.nrml.logic_tree import NrmlDocument
from nzshm_model.source_logic_tree.toshi_api import get_secret

# Get API key from AWS secrets manager
API_URL = os.getenv('NZSHM22_TOSHI_API_URL', "http://127.0.0.1:5000/graphql")
try:
    if 'TEST' in API_URL.upper():
        API_KEY = get_secret("NZSHM22_TOSHI_API_SECRET_TEST", "us-east-1").get("NZSHM22_TOSHI_API_KEY_TEST")
    elif 'PROD' in API_URL.upper():
        API_KEY = get_secret("NZSHM22_TOSHI_API_SECRET_PROD", "us-east-1").get("NZSHM22_TOSHI_API_KEY_PROD")
    else:
        API_KEY = os.getenv('NZSHM22_TOSHI_API_KEY', "")
except AttributeError as err:
    print(f"unable to get secret from secretmanager: {err}")
    API_KEY = os.getenv('NZSHM22_TOSHI_API_KEY', "")
S3_URL = None
DEPLOYMENT_STAGE = os.getenv('DEPLOYMENT_STAGE', 'LOCAL').upper()
REGION = os.getenv('REGION', 'ap-southeast-2')  # SYDNEY


class SourceSolution(ToshiFile):
    def get_source(self, fid):

        qry = '''
        query file ($id:ID!) {
            node(id: $id) {
                __typename
                ... on FileInterface {
                  file_name
                  file_size
                  meta {k v}
                }
                ... on ScaledInversionSolution {
                  meta{ k k}
                  source_solution {
                    meta {k v}
                  }
                }
            }
        }
        '''
        # print(qry)
        input_variables = dict(id=fid)
        executed = self.run_query(qry, input_variables)
        return executed['node']


def rupt_set_from_meta(meta):
    for itm in meta:
        if itm['k'] == "rupture_set_file_id":
            return itm['v']


def fetch_toshi_source(destination, file_id, file_prefix=""):
    headers = {"x-api-key": API_KEY}
    api = SourceSolution(API_URL, S3_URL, None, with_schema_validation=False, headers=headers)

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


class PshaAdapterInterface(ABC):
    """
    Defines methods to be provided by a PSHA adapter class implementation.
    """

    def __init__(self, source_logic_tree):
        self._source_logic_tree = source_logic_tree

    @abstractmethod
    def fetch_resources(self, target_folder):
        pass  # raise NotImplementedError()

    @abstractmethod
    def write_config(self, target_folder: Union[pathlib.Path, str]) -> pathlib.Path:
        pass  # raise NotImplementedError()


class OpenquakeSimpleSourceNrml(PshaAdapterInterface):
    """
    Openquake simple NRML represention
    """

    def write_config(self, target_folder: Union[pathlib.Path, str]) -> pathlib.Path:
        destination = pathlib.Path(target_folder)
        assert destination.exists()
        assert destination.is_dir()

        ## TODO implement XML writer
        print(dir(self.config()))
        assert 0

        target_file = pathlib.Path(destination, 'sources.xml')
        with open(target_file, 'w') as fout:
            fout.write(self.config())
        return target_file

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
                    if long_filenames:
                        # flatten the paths
                        file_prefix = str(um.path().parent).replace('/', "_")
                        destination = pathlib.Path(target_folder)  # / current_model.version
                        # fetch em
                        fetch_toshi_source(destination, file_id=um.path().name, file_prefix=file_prefix)
                    else:
                        # otherwise use folders
                        destination = pathlib.Path(target_folder) / um.path().parent
                        fetch_toshi_source(destination, file_id=um.path().name)

    def config(self):
        return NrmlDocument.from_model_slt(self._source_logic_tree).logic_trees[0]


@dataclass
class BranchAttributeSpec:
    name: str
    long_name: str
    value_options: List[Any] = field(default_factory=list)


@dataclass(frozen=True)
class BranchAttributeValue:
    name: str
    long_name: str
    value: Any = None

    @staticmethod
    def from_branch_attribute(ba: BranchAttributeSpec, value):
        return BranchAttributeValue(ba.name, ba.long_name, value)

    @staticmethod
    def all_from_branch_attribute(ba: BranchAttributeSpec):
        for opt in ba.value_options:
            yield BranchAttributeValue(ba.name, ba.long_name, opt)

    def __repr__(self):
        return f"{self.name}{self.value}"


@dataclass
class Branch:
    values: List[BranchAttributeValue]
    weight: float = 1.0
    onfault_nrml_id: Union[str, None] = ""
    distributed_nrml_id: Union[str, None] = ""
    inversion_solution_id: Union[str, None] = ""
    inversion_solution_type: Union[str, None] = ""
    rupture_set_id: Union[str, None] = ""


@dataclass
class FaultSystemLogicTreeSpec:
    short_name: str
    long_name: str
    branches: List['BranchAttributeValue'] = field(default_factory=list)


@dataclass
class FaultSystemLogicTree:
    short_name: str
    long_name: str
    branches: List['Branch'] = field(default_factory=list)

    def validate_weights(self) -> bool:
        weight = 0.0
        for b in self.branches:
            weight += b.weight
        return weight == 1.0

    def derive_spec(self) -> FaultSystemLogicTreeSpec:
        fslt_spec = FaultSystemLogicTreeSpec(short_name=self.short_name, long_name=self.long_name)

        options: Dict[str, set] = {}

        # extract unique values in to options
        for branch in self.branches:
            # iterate all the branches, yielding the unique  branch options
            # print('branch', branch)
            for value in branch.values:
                if value.name not in options.keys():
                    options[value.name] = set([])
                val = value.value
                if isinstance(val, list):  # make it hashable
                    val = tuple(val)
                bao = BranchAttributeValue(value.name, value.long_name, val)
                options[value.name].add(bao)

        # print(options)

        def option_values(options: Dict) -> Generator:
            # boil down the options values
            ret = {}
            for key, opt in options.items():
                if key not in ret:
                    ret[key] = BranchAttributeSpec(key, list(opt)[0].long_name)

                values = []
                for val in opt:
                    values.append(val.value)
                ret[key].value_options = sorted(values)

            for key, bas in ret.items():
                yield bas

        fslt_spec.branches = list(option_values(options))

        return fslt_spec


@dataclass
class SourceLogicTreeCorrelation:
    primary_short_name: str
    secondary_short_name: str
    primary_values: List[BranchAttributeValue]
    secondary_values: List[BranchAttributeValue]

    # these methods enforce set compairson
    def is_primary(self, bavs: Iterable[BranchAttributeValue]) -> bool:
        return all([item in self.primary_values for item in bavs])

    def is_secondary(self, bavs: Iterable[BranchAttributeValue]) -> bool:
        return all([item in self.secondary_values for item in bavs])


@dataclass
class SourceLogicTreeSpec:
    fault_system_lts: List[FaultSystemLogicTreeSpec] = field(default_factory=list)


@dataclass
class SourceLogicTree:
    version: str
    title: str
    fault_system_lts: List[FaultSystemLogicTree] = field(default_factory=list)
    correlations: List[SourceLogicTreeCorrelation] = field(
        default_factory=list
    )  # to use for selecting branches and re-weighting when logic trees are correlated

    def derive_spec(self) -> SourceLogicTreeSpec:
        slt_spec = SourceLogicTreeSpec()
        for fslt in self.fault_system_lts:
            slt_spec.fault_system_lts.append(FaultSystemLogicTree.derive_spec(fslt))
        return slt_spec

    def psha_adapter(self, provider: Type[PshaAdapterInterface] = OpenquakeSimpleSourceNrml, **kwargs):
        return provider(self)


@dataclass
class CompositeBranch:
    """Combination of all fault type branches"""

    branches: List[Branch]
    weight: float = 1.0

    def __post_init__(self) -> None:
        self.weight = reduce(mul, [branch.weight for branch in self.branches])


@dataclass
class FlattenedSourceLogicTree:
    """Flattened source logic tree containing all CompositeBranch combinations"""

    version: str
    title: str
    branches: List[CompositeBranch]

    def __post_init__(self) -> None:
        total_weight = reduce(add, [branch.weight for branch in self.branches])
        if not isclose(total_weight, 1.0):
            raise Exception('logic tree weights do not add to 1.0 (sum is %s)' % total_weight)

    @classmethod
    def from_source_logic_tree(cls, slt: SourceLogicTree):

        slt_copy = deepcopy(slt)  # don't want to change weights of origional logic tree object
        branches = [fslt.branches for fslt in slt_copy.fault_system_lts]

        def yield_cor(branches, slt_copy):
            nnames = [[faultsys_lt.short_name] * len(faultsys_lt.branches) for faultsys_lt in slt_copy.fault_system_lts]
            for cb, names in zip(product(*branches), product(*nnames)):
                has_correlation = False
                for cor in slt_copy.correlations:
                    sindex = names.index(cor.secondary_short_name)
                    if cor.is_secondary(cb[sindex].values):
                        has_correlation = True
                        pindex = names.index(cor.primary_short_name)
                        if cor.is_primary(cb[pindex].values):
                            cb[sindex].weight = 1.0
                            yield CompositeBranch(list(cb))
                if not has_correlation:
                    yield CompositeBranch(list(cb))

        if slt.correlations:
            return cls(slt.version, slt.title, list(yield_cor(branches, slt_copy)))
        else:
            return cls(slt.version, slt.title, [CompositeBranch(list(cb)) for cb in product(*branches)])

    def __repr__(self):
        return f'{self.__class__} title {self.title} number of branches: {len(self.branches)}'
