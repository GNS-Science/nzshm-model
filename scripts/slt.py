"""Script to build an SLT dict/json for K-API from a source_logic_tree model."""

# import argparse
import click
import logging
import sys
import json
import dataclasses
from pathlib import Path

import nzshm_model
from nzshm_model import get_model_version
from nzshm_model.source_logic_tree.logic_tree import SourceLogicTree, FaultSystemLogicTree, Branch

from nzshm_model.source_logic_tree.slt_config import from_config

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logging.getLogger('nshm_toshi_client.toshi_client_base').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('gql.transport.requests').setLevel(logging.WARN)

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
screen_handler = logging.StreamHandler(stream=sys.stdout)
screen_handler.setFormatter(formatter)
file_handler = logging.FileHandler('thh.log')
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

    for version in nzshm_model.versions:
        if not long:
            click.echo(version['id'])
            continue
        click.echo(f"{version['id']} `{version['title']}`")

@slt.command(name='model')
@click.argument('model_id')
@click.option('-v', '--verbose', is_flag=True)
def cli_model(model_id, verbose):
    """Get a model by MODEL_ID."""
    model = get_model_version(model_id)['model']
    slt = SourceLogicTree(fault_system_branches=[model.build_crustal_branches()])

    j = json.dumps(dataclasses.asdict(slt), indent=4)
    click.echo(j)


@slt.command(name='from_config')
@click.argument('config_path')
@click.option('-v', '--verbose', is_flag=True)
def cli_from_config(config_path, verbose):
    """Convert a python config file at CONFIG_PATH to an SLT model."""

    fslt = from_config(config_path)
    j = json.dumps(dataclasses.asdict(fslt), indent=4)
    click.echo(j)


def process(args):
    """Do the work."""
    pass


if __name__ == '__main__':
    slt()  # pragma: no cover
