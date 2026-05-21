try:
    from nshm_toshi_client import ToshiFile

except (ModuleNotFoundError, ImportError):
    print("WARNING: optional `toshi` dependencies are not installed.")
    raise


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
