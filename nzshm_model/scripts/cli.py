"""Console script for model users...."""

# noqa
import logging
import os

import click

import nzshm_model

# from nzshm_model.source_logic_tree import SourceLogicTree
import nzshm_model.logic_tree
from nzshm_model.logic_tree.source_logic_tree import SourceLogicTree
from nzshm_model.logic_tree.source_logic_tree.version1.slt_config import from_config

# from nzshm_model.source_logic_tree.slt_config import from_config, resolve_toshi_source_ids  # noqa
from nzshm_model.psha_adapter.openquake import OpenquakeSourcePshaAdapter

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logging.getLogger('nshm_toshi_client.toshi_client_base').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('gql.transport.requests').setLevel(logging.WARN)

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
root_handler = log.handlers[0]
root_handler.setFormatter(formatter)

log.debug('DEBUG message')
log.info('INFO message')


#  _ __ ___   __ _(_)_ __
# | '_ ` _ \ / _` | | '_ \
# | | | | | | (_| | | | | |
# |_| |_| |_|\__,_|_|_| |_|
@click.group()
def cli():
    """Nzshm-model helpers for model consumers."""


@cli.command()
@click.option('--cache_folder', '-w', default=lambda: os.getcwd())
@click.option('--model_id', '-m', default="NSHM_v1.0.4")
# @click.option('--long_filenames', '-lf', is_flag=True, help="use long filenames, instead of folders")
def fetch(cache_folder, model_id):
    """Fetch SLT sources from toshi"""
    click.echo(f"work folder: {cache_folder}")
    click.echo(f"model_id: {model_id}")

    model = nzshm_model.get_model_version(model_id)
    adapter = model.source_logic_tree().psha_adapter(provider=OpenquakeSourcePshaAdapter)

    for item in adapter.fetch_resources(cache_folder):
        click.echo(item)

    click.echo('DONE')


@cli.command()
@click.argument('module-path')
@click.argument('json-path')
@click.option('--title', '-t')
@click.option('--version', '-v')
def convert(module_path, json_path, title, version):
    """Convert an old-style source logic tree defined as a python module to a new style
    JSON logic tree file.
    """

    slt_v1 = from_config(module_path, version=version, title=title)
    slt = SourceLogicTree.from_source_logic_tree(slt_v1)
    slt.to_json(json_path)


@cli.command()
@click.option('--cache_folder', '-w', default=lambda: os.getcwd())
@click.option('--output_folder', '-o', default=lambda: os.getcwd())
@click.option('--model_id', '-m', default="NSHM_v1.0.4")
def unpack(cache_folder, output_folder, model_id):

    model = nzshm_model.get_model_version(model_id)
    adapter = model.source_logic_tree().psha_adapter(provider=OpenquakeSourcePshaAdapter)
    source_map = adapter.unpack_resources(cache_folder, output_folder)
    click.echo(len(source_map.items()))
    click.echo('DONE')


@cli.command()
@click.option('--cache_folder', '-w', default=lambda: os.getcwd())
@click.option('--output_folder', '-o', default=lambda: os.getcwd())
@click.option('--model_id', '-m', default="NSHM_v1.0.4")
def config(cache_folder, output_folder, model_id):
    """Write an openquake hazard configuration

    This is a work in progress, as it only handles the Source LT, and not GMM LT
    or general configuration.
    """

    model = nzshm_model.get_model_version(model_id)
    slt = model.source_logic_tree  # always version 2

    ## example filter functions
    def unscaled_filter(obj):
        for v in obj.values:
            if v.name == 's' and v.value == 1.0:  # moment rate scaling
                return True

    def geodetic_filter(obj):
        for v in obj.values:
            if v.long_name == 'deformation model' and v.value == "geodetic":
                return True

    slt = SourceLogicTree.from_branches((fb for fb in slt if unscaled_filter(fb) and geodetic_filter(fb)))

    adapter = slt.psha_adapter(provider=OpenquakeSourcePshaAdapter)

    adapter.write_config(cache_folder, output_folder)
    click.echo('DONE')


if __name__ == "__main__":
    cli()  # pragma: no cover
