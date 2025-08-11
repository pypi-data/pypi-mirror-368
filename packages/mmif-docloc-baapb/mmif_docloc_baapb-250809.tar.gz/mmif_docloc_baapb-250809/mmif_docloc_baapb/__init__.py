import requests
import os

RESOVLER_ADDRESS_ENVVAR = 'BAAPB_RESOLVER_ADDRESS'
if RESOVLER_ADDRESS_ENVVAR in os.environ:
    RESOLVER_ADDRESS = os.environ[RESOVLER_ADDRESS_ENVVAR]
else:
    RESOLVER_ADDRESS = 'localhost:5000'


def resolve(docloc):
    scheme = 'baapb'
    if docloc.startswith(f'{scheme}://'):
        guid, document_type = docloc[len(scheme)+3:].rsplit('.', 1)
        url = 'http://' + RESOLVER_ADDRESS + '/searchapi'
        r = requests.get(url, params={'guid': guid, 'file':document_type})
        if 199 < r.status_code < 299:
            # when there are multiple files with the query guid, just return the first one
            return r.json()[0]
        else:
            raise ValueError(f'cannot resolve document location: "{docloc}", '
                             f'is the resolver running at "{RESOLVER_ADDRESS}"?')
    else:
        raise ValueError(f'cannot handle document location scheme: "{docloc}"')

if __name__ == '__main__':
    import sys
    print(resolve(sys.argv[1]))

