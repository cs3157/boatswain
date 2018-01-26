
import os

GITHUB_DEFAULT_PATH = os.path.expanduser('~/.github.auth')

def read_token_file(filename):
    with open(os.path.expanduser(filename)) as f:
        return f.read().rstrip()
