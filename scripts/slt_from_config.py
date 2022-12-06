"""Script to build an SLT dict/json for K-API from a source_logic_tree model."""

import argparse
from pathlib import Path

import nzshm_model
from nzshm_model import get_model_version


def process(args):
    """Do the work."""
    pass
    model = get_model_version(nzshm_model, args.model_version)
    print (f'model {model}')

def parse_args():
    parser = argparse.ArgumentParser(
        description='slt_from_config.py- extract a source_logic_tree from a valid configuration.'
    )
    parser.add_argument('model_version', help='a valid model_version.')
    parser.add_argument('source_id', help='source id.')

    args = parser.parse_args()
    return args


def handle_args(args):
    process(args)


def main():
    handle_args(parse_args())


if __name__ == '__main__':
    main()  # pragma: no cover
