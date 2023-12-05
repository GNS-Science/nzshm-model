"""Console script for model users...."""
# noqa
import logging
import os
import pathlib
import sys

import click

import nzshm_model
# from nzshm_model.source_logic_tree.slt_config import from_config, resolve_toshi_source_ids  # noqa
from nzshm_model.psha_adapter import OpenquakeSimplePshaAdapter

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
@click.option('--long_filenames', '-lf', is_flag=True, help="use long filenames, instead of folders")
def fetch(work_folder, model_id, long_filenames):
    """Fetch SLT sources from toshi"""
    click.echo(f"work folder: {work_folder}")
    click.echo(f"model_id: {model_id}")

    model = nzshm_model.get_model_version(model_id)

    model.source_logic_tree()\
        .psha_adapter(provider=OpenquakeSimplePshaAdapter)\
        .fetch_resources(work_folder, long_filenames)

    click.echo('DONE')


@cli.command()
@click.option('--work_folder', '-w', default=lambda: os.getcwd())
@click.option('--model_id', '-m', default="NSHM_v1.0.4")
@click.option('--long_filenames', '-lf', is_flag=True, help="use long filenames, instead of folders")
def psha_config(work_folder, model_id, long_filenames):
    """write a psha config"""
    click.echo(f"work folder: {work_folder}")
    click.echo(f"model_id: {model_id}")

    model = nzshm_model.get_model_version(model_id)

    destination = pathlib.Path(work_folder)
    assert destination.exists()
    assert destination.is_dir()
    destination.mkdir(parents=True, exist_ok=True)

    model.source_logic_tree()\
        .psha_adapter(provider=OpenquakeSimplePshaAdapter,
                      help="future there may be multiple adapters")\
        .write_config(destination)
    click.echo('DONE')


if __name__ == "__main__":
    cli()  # pragma: no cover
