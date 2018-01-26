#!/usr/bin/env python3

import sys
import requests
import argparse
import env_auth
import githublib as ghl


def parse_args(args):
    parser = argparse.ArgumentParser(description='Add collaborators to repo')

    parser.add_argument('-f', '--token-file',
                        default=env_auth.GITHUB_DEFAULT_PATH,
                        type=argparse.FileType('rU'),
                        help='file path for GitHub auth token [{}]'.format(
                            env_auth.GITHUB_DEFAULT_PATH),
                        metavar='<path>',
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

    return parser.parse_args()


def do_add_collaborators(owner, repo, user, perm, token, noop=False,
        verbose=True):
    #
    # Construct request params
    #
    uri, data = ghl.add_collaborator(owner, repo, user, permission=perm)
    url = ghl.format_url(uri)
    headers = ghl.auth_header(token)

    #
    # Perform action
    #
    if noop:
        print('noop flag specified, not sending request to GitHub:')
        print('\trequest url: {}'.format(url))
        print('\trequest data: {}'.format(data))
        print('\trequest headers: {}'.format(headers))

    else:
        r = requests.put(url, headers=headers, data=data)
        d = r.json()
        if verbose:
            print('{ter} invited {tee} to {repo} as collaborator'.format(
                    ter=d['inviter']['login'],
                    tee=d['invitee']['login'],
                    repo=d['repository']['full_name'],
            ))
            print('permissions: {perm}'.format(perm=d['permissions']))
            print('invitation url: {url}'.format(url=d['url']))


def main(args=None, verbose=True):
    if args is None:
        args = sys.argv
    
    opt = parse_args(args)

    token = env_auth.read_token_file(opt.token_file.name)

    if verbose:
        print('adding {user} to {owner}/{repo} as collaborator'.format(
            user=opt.user,
            owner=opt.owner,
            repo=opt.repo,
        ))
        print('\twith "{perm}" permissions...'.format(perm=opt.permission))
        print()

    do_add_collaborators(opt.owner, opt.repo, opt.user, opt.permission, token,
            noop=opt.noop, verbose=verbose)

if __name__ == '__main__':
    main()
