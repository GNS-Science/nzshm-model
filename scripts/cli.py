"""Console script for model users...."""
# noqa
import logging
import os
import pathlib
import sys
import zipfile

import click
from nshm_toshi_client.toshi_file import ToshiFile

import nzshm_model
from nzshm_model.source_logic_tree.logic_tree import SourceLogicTree  # noqa
from nzshm_model.source_logic_tree.slt_config import from_config, resolve_toshi_source_ids  # noqa
from nzshm_model.source_logic_tree.toshi_api import get_secret

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('nshm_toshi_client.toshi_client_base').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('gql.transport.requests').setLevel(logging.WARN)

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
screen_handler = logging.StreamHandler(stream=sys.stdout)
screen_handler.setFormatter(formatter)
log.addHandler(screen_handler)

log.debug('DEBUG message')
log.info('INFO message')

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


def fetch_toshi_source(destination, file_id, file_prefix):
    headers = {"x-api-key": API_KEY}
    api = SourceSolution(API_URL, S3_URL, None, with_schema_validation=False, headers=headers)

    click.echo(f'checking {file_id}')
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
        prefixed = pathlib.Path(destination, f"{file_prefix}_{name}")
        extracted.rename(prefixed)

    # delete the zipfiles
    fname.unlink()


def fetch_and_unpack_sources(work_folder, current_model):

    logic_tree = current_model.source_logic_tree_nrml()
    for branch_set in logic_tree.branch_sets:
        click.echo(f"branch set {branch_set.branchSetID}")
        for branch in branch_set.branches:
            click.echo(f"branch: {branch.branchID}")
            for um in branch.uncertainty_models:
                # flatten the paths

                file_prefix = str(um.path().parent).replace('/', "_")
                destination = pathlib.Path(work_folder) / current_model.version
                # fetch em
                fetch_toshi_source(destination, file_id=um.path().name, file_prefix=file_prefix)


#  _ __ ___   __ _(_)_ __
# | '_ ` _ \ / _` | | '_ \
# | | | | | | (_| | | | | |
# |_| |_| |_|\__,_|_|_| |_|
@click.group()
def cli():
    """Nzshm-model tasks."""


@cli.command()
@click.option('--work_folder', '-w', default=lambda: os.getcwd())
@click.option('--model_id', '-m', default="NSHM_v1.0.4")
def fetch(work_folder, model_id):
    """Fetch SLT sources from toshi"""
    click.echo(f"work folder: {work_folder}")
    click.echo(f"model_id: {model_id}")

    model = nzshm_model.get_model_version(model_id)

    solution = fetch_and_unpack_sources(work_folder, model)  # noqa


if __name__ == "__main__":
    cli()  # pragma: no cover
