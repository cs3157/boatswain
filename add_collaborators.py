#!/usr/bin/env python3

import requests
import argparse
import githublib as ghl

#
# Parse arguments
#
parser = argparse.ArgumentParser(description='Add collaborators to repo')

parser.add_argument('-f', '--token-file',
                    default='.github.auth',
                    type=argparse.FileType('rU'),
                    help='file path for GitHub Personal Access Token [.github.auth]',
                    metavar='<path>'
)

parser.add_argument('owner',
                    type=str,
                    help='repo owner',
                    metavar='<repo-owner>',
)

parser.add_argument('repo',
                    type=str,
                    help='repo name',
                    metavar='<repo-name>',
)

parser.add_argument('user',
                    type=str,
                    help='user name',
                    metavar='<user>',
)

parser.add_argument('--permission',
                    type=str,
                    default='pull',
                    help='do not submit anything',
                    metavar='push|pull|admin',
)


parser.add_argument('-n', '--noop',
                    default=False,
                    action='store_true',
                    help='do not submit anything',
)

args = parser.parse_args()


#
# Set variables
#
with open(args.token_file.name) as f:
    token = f.read().rstrip()

owner, repo, user, perm = args.owner, args.repo, args.user, args.permission


#
# Some reporting
#
print('adding {user} to {owner}/{repo} as collaborator'.format(
            user=user,
            owner=owner,
            repo=repo,
))
print('\twith "{perm}" permissions...'.format(perm=perm))
print()


#
# Construct request params
#
uri, data = ghl.add_collaborator(owner, repo, user, permission=perm)
url = ghl.format_url(uri)
headers = ghl.auth_header(token)


#
# Perform action
#
if args.noop:
    print('noop flag specified, not sending request to GitHub:')
    print('\trequest url: {}'.format(url))
    print('\trequest data: {}'.format(data))
    print('\trequest headers: {}'.format(headers))

else:
    r = requests.put(url, headers=headers, data=data)
    d = r.json()
    print('{inviter} invited {invitee} to {repo} as collaborator'.format(
        inviter=d['inviter']['login'],
        invitee=d['invitee']['login'],
        repo=d['repository']['full_name'],
    ))
    print('permissions: {perm}'.format(perm=d['permissions']))
    print('invitation  url: {url}'.format(url=d['url']))
