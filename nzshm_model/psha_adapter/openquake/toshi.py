import os

import botocore.exceptions

try:
    from nshm_toshi_client.toshi_file import ToshiFile

    from nzshm_model.logic_tree.source_logic_tree.toshi_api import get_secret
except (ModuleNotFoundError, ImportError):
    print("WARNING: optional `toshi` dependencies are not installed.")
    raise

# Get API key from AWS secrets manager
API_URL = os.getenv('NZSHM22_TOSHI_API_URL', "http://127.0.0.1:5000/graphql")
try:
    if 'TEST' in API_URL.upper():
        API_KEY = get_secret("NZSHM22_TOSHI_API_SECRET_TEST", "us-east-1").get("NZSHM22_TOSHI_API_KEY_TEST")
    elif 'PROD' in API_URL.upper():
        API_KEY = get_secret("NZSHM22_TOSHI_API_SECRET_PROD", "us-east-1").get("NZSHM22_TOSHI_API_KEY_PROD")
    else:
        API_KEY = os.getenv('NZSHM22_TOSHI_API_KEY', "")
except (AttributeError, botocore.exceptions.EndpointConnectionError) as err:
    print(f"unable to get secret from secretmanager: {err}")
    API_KEY = os.getenv('NZSHM22_TOSHI_API_KEY', "")

# S3_URL = None
# DEPLOYMENT_STAGE = os.getenv('DEPLOYMENT_STAGE', 'LOCAL').upper()
# REGION = os.getenv('REGION', 'ap-southeast-2')  # SYDNEY


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
            }
        }
        '''
        # print(qry)
        input_variables = dict(id=fid)
        executed = self.run_query(qry, input_variables)
        return executed['node']
