#! python toshi_api.py

"""
enrich SLT from TOSHI_API.

"""

import base64
import json
import os

import boto3
from botocore.exceptions import ClientError
from nshm_toshi_client.toshi_client_base import ToshiClientBase

API_URL = os.getenv('NZSHM22_TOSHI_API_URL', "http://127.0.0.1:5000/graphql")

# TODO this shojld be define in an AWS helper library  - it's used everywhere
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
        return executed['node']


if 'TEST' in API_URL.upper():
    API_KEY = get_secret("NZSHM22_TOSHI_API_SECRET_TEST", "us-east-1").get("NZSHM22_TOSHI_API_KEY_TEST")
elif 'PROD' in API_URL.upper():
    API_KEY = get_secret("NZSHM22_TOSHI_API_SECRET_PROD", "us-east-1").get("NZSHM22_TOSHI_API_KEY_PROD")
else:
    API_KEY = os.getenv('NZSHM22_TOSHI_API_KEY', "")
headers = {"x-api-key": API_KEY}
toshi_api = ToshiApi(API_URL, None, with_schema_validation=False, headers=headers)


def resolve_source_id_nrml(nrml_id: str):

    source = toshi_api.get_source_from_nrml(nrml_id)
    return source


if __name__ == "__main__":

    from pathlib import Path

    from nzshm_model.source_logic_tree.slt_config import from_config

    config_path = Path(__file__).parent / 'SLT_v8_gmm_v2_final.py'
    slt = from_config(config_path)

    for fslt in slt.fault_system_branches:
        for branch in fslt.branches:
            print(branch)
            print(resolve_source_id_nrml(branch.inversion_source))
