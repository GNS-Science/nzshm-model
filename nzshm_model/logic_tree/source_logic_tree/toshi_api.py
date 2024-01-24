#! python toshi_api.py

"""
enrich SLT from TOSHI_API.
"""

import base64
import dataclasses
import json
import os
from typing import Dict, List, Optional, Union

import boto3
from botocore.exceptions import ClientError
from nshm_toshi_client.toshi_client_base import ToshiClientBase

API_URL = os.getenv('NZSHM22_TOSHI_API_URL', "http://127.0.0.1:5000/graphql")


# TODO this should be define in an AWS helper library  - it's used everywhere
def get_secret(secret_name, region_name):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        else:
            return base64.b64decode(get_secret_value_response['SecretBinary'])


@dataclasses.dataclass
class InversionInfo:
    typename: Union[str, None] = None
    solution_id: Union[str, None] = None


class SourceSolutionMap:
    """A mapping between nrml ids and hazard solution ids"""

    def __init__(self, hazard_jobs: List[dict] = []) -> None:
        self._dict: Dict[str, str] = {}
        if hazard_jobs:
            for job in hazard_jobs:
                for arg in job['node']['child']['arguments']:
                    if arg['k'] == 'logic_tree_permutations':
                        branch_info = json.loads(arg['v'].replace("'", '"'))[0]['permute'][0]['members'][0]
                        onfault_nrml_id = branch_info['inv_id']
                        distributed_nrml_id = branch_info['bg_id']
                hazard_solution = job['node']['child']['hazard_solution']
                self._dict[self.__key(onfault_nrml_id, distributed_nrml_id)] = hazard_solution['id']

    def append(self, other: 'SourceSolutionMap'):
        self._dict.update(other._dict)

    def get_solution_id(self, *, onfault_nrml_id: str, distributed_nrml_id: str) -> Optional[str]:
        return self._dict.get(self.__key(onfault_nrml_id, distributed_nrml_id))

    @staticmethod
    def __key(onfault_nrml_id: str, distributed_nrml_id: str) -> str:
        return ':'.join((str(onfault_nrml_id), str(distributed_nrml_id)))


class ToshiApi(ToshiClientBase):
    def get_source_from_nrml(self, nrml_id):
        qry = '''
        query nrml ($nrml_id: ID!) {
          node(id: $nrml_id) {
            __typename
            ... on InversionSolutionNrml {
              file_name
              source_solution {
                __typename
                ... on Node { id }
              }
            }
          }
        }'''

        # print(qry)
        input_variables = dict(nrml_id=nrml_id)
        executed = self.run_query(qry, input_variables)
        return (
            InversionInfo(
                typename=executed['node']['source_solution']['__typename'],
                solution_id=executed['node']['source_solution']['id'],
            )
            if executed.get('node')
            else InversionInfo()
        )

    def get_rupture_set_id(self, solution_id):
        qry = '''
        query file0 ($id: ID!) {
          node(id: $id) {
            __typename
            ... on PredecessorsInterface {
              predecessors {
                id
                typename
                relationship
                depth
                file_node: node {
                  __typename
                  ... on Node {id}
                  ... on File {
                    file_name
                  }
                }
              }
            }
          }
        }
        '''
        # print(qry)
        input_variables = dict(id=solution_id)
        # print(input_variables)
        executed = self.run_query(qry, input_variables)
        return executed['node']


if 'TEST' in API_URL.upper():
    API_KEY = get_secret("NZSHM22_TOSHI_API_SECRET_TEST", "us-east-1").get("NZSHM22_TOSHI_API_KEY_TEST")
elif 'PROD' in API_URL.upper():
    API_KEY = get_secret("NZSHM22_TOSHI_API_SECRET_PROD", "us-east-1").get("NZSHM22_TOSHI_API_KEY_PROD")
else:
    API_KEY = os.getenv('NZSHM22_TOSHI_API_KEY', "")
headers = {"x-api-key": API_KEY}
toshi_api = ToshiApi(API_URL, None, with_schema_validation=False, headers=headers)


def solution_rupt_set_id(solution_id) -> str:
    data = toshi_api.get_rupture_set_id(solution_id)
    for itm in data['predecessors']:
        if itm["typename"] == "File":
            return itm['file_node']['id']
    return ""


if __name__ == "__main__":
    """This should be a test!"""
    import dataclasses
    from pathlib import Path

    from nzshm_model.source_logic_tree.slt_config import from_config

    SKIP_FS_NAMES = ['SLAB', 'HIK']  # , 'CRU'

    config_path = Path(__file__).parent / 'SLT_v8_gmm_v2_final.py'
    slt = from_config(config_path)

    for fslt in slt.fault_system_lts:
        if fslt.short_name in SKIP_FS_NAMES:  # CRU
            continue
        for branch in fslt.branches[-2:]:
            nrml_info = toshi_api.get_source_from_nrml(branch.onfault_nrml_id)
            print(nrml_info)
            branch.inversion_solution_id = nrml_info.solution_id
            branch.inversion_solution_type = nrml_info.typename
            branch.rupture_set_id = solution_rupt_set_id(nrml_info.solution_id)
            print(branch)  # , end='', flush=True)

    j = json.dumps(dataclasses.asdict(slt), indent=4)
    # print(j)
