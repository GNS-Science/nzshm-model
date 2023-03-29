"""Script to build an SLT dict/json for K-API from a source_logic_tree model."""

import dataclasses
import json
import logging
import sys

import click

import nzshm_model
from nzshm_model import get_model_version
from nzshm_model.source_logic_tree.logic_tree import SourceLogicTree
from nzshm_model.source_logic_tree.slt_config import from_config, resolve_toshi_source_ids

log = logging.getLogger()
logging.basicConfig(level=logging.WARN)
logging.getLogger('nshm_toshi_client.toshi_client_base').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('gql.transport.requests').setLevel(logging.WARN)

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
screen_handler = logging.StreamHandler(stream=sys.stdout)
screen_handler.setFormatter(formatter)
file_handler = logging.FileHandler('slt.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
log.addHandler(screen_handler)
log.addHandler(file_handler)


@click.group()
def slt():
    pass


@slt.command(name='ls')
@click.option('-l', '--long', is_flag=True)
def cli_ls(long):
    """List the available model versions."""

    for version in nzshm_model.versions.keys():
        if not long:
            click.echo(version)
            continue
        model = nzshm_model.get_model_version(version)
        click.echo(f"{model.version} `{model.source_logic_tree().title}`")


@slt.command(name='model')
@click.argument('model_id')
@click.option('-B', '--build', is_flag=True)
def cli_model(model_id, build):
    """Get a model by MODEL_ID."""
    model = get_model_version(model_id)
    slt = (
        SourceLogicTree(version="0", title="", fault_system_lts=[model.build_crustal_branches()])
        if build
        else model.source_logic_tree()
    )
    j = json.dumps(dataclasses.asdict(slt), indent=4)
    click.echo(j)


@slt.command(name='from_config')
@click.argument('config_path')
@click.argument('version')
@click.argument('title')
@click.option('-R', '--resolve_toshi_ids', is_flag=True)
def cli_from_config(config_path, version, title, resolve_toshi_ids):
    """Convert a python config file at CONFIG_PATH to an SLT model. Both VERSION and TITLE are required."""

    slt = from_config(config_path, version, title)

    if resolve_toshi_ids:
        slt = resolve_toshi_source_ids(slt)  # get new slt with toshi_ids
    j = json.dumps(dataclasses.asdict(slt), indent=4)
    click.echo(j)


@slt.command(name='spec')
@click.argument('model_id')
@click.option('-B', '--build', is_flag=True)
def cli_model_spec(model_id, build):
    """Get a model specification by MODEL_ID."""
    model = get_model_version(model_id)
    slt = (
        SourceLogicTree(version="0", title="", fault_system_lts=[model.build_crustal_branches()])
        if build
        else model.source_logic_tree()
    )
    j = json.dumps(dataclasses.asdict(slt.derive_spec()), indent=4)
    click.echo(j)


if __name__ == '__main__':
    slt()  # pragma: no cover
