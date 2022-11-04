#!/usr/bin/env python3

import sys
import boatswain_env as benv
from github import Github

CMD_NAME = 'add_collaborator'
DESC = 'Add user as collaborator to GitHub repo'

def add_collaborator_deco(parser):
    parser.add_argument('owner',
                        type=str,
                        help='repo owner (individual or organization)',
                        metavar='<repo-owner>',
    )

    parser.add_argument('repo',
                        type=str,
                        help='repo name',
                        metavar='<repo-name>',
    )

    parser.add_argument('user',
                        type=str,
                        help='user name of user to be added',
                        metavar='<user>',
    )

    parser.add_argument('permission',
                        type=str,
                        help='permissions of user to be added',
                        metavar='push|pull|admin',
    )


def do_add_collaborator(repo, user, permission, opt):

    opt.info(f'Adding {user} as collaborator to {repo.full_name} with {permission} permissions')

    if opt.noop:
        opt.log('--noop option specified; not adding collaborator')
        return

    repo.add_to_collaborators(user, permission=permission)

    opt.info(f'User {user} successfully added')


def add_collaborator(opt):
    g = Github(opt.githubToken())
    repo_full_name = f'{opt.owner}/{opt.repo}'
    repo = g.get_repo(repo_full_name)

    if not opt.promptYes((f'Are you sure you would like to add {user} '
                            f'as a collaborator to {repo_full_name} with {permission} permissions?'),
                        True):
        opt.warn('Aborting')
        return

    do_add_collaborator(repo, opt.user, opt.permission, opt)


def main(args=None, config_path=None):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=add_collaborator_deco, req_github=True)

    add_collaborator(opt)


if __name__ == '__main__':
    main()
