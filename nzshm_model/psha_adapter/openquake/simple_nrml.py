import os
import pathlib
import zipfile
from typing import Union

from nshm_toshi_client.toshi_file import ToshiFile

from nzshm_model.psha_adapter.openquake.logic_tree import NrmlDocument
from nzshm_model.psha_adapter.psha_adapter_interface import PshaAdapterInterface
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


class OpenquakeSimplePshaAdapter(PshaAdapterInterface):
    """
    Openquake PSHA simple nrml support.
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
