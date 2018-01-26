
import json

def format_url(uri):
    return 'https://api.github.com{}'.format(uri)

def auth_header(token):
    return {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'token {}'.format(token),
    }


def add_collaborator(owner, repo, username, permission='pull'):
    uri = '/repos/{owner}/{repo}/collaborators/{username}'.format(
            owner=owner,
            repo=repo,
            username=username,
    )
    data = {
            'permission': permission,
    }
    return uri, json.dumps(data)
