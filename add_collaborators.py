#!/usr/bin/env python3

import sys
import boatswain_env as benv
import argparse
from github import Github
from add_collaborator import do_add_collaborator

CMD_NAME = 'add_collaborators'
DESC = 'Add multiple users as collaborator to GitHub repo'

def add_collaborators_deco(parser):
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

    parser.add_argument('users',
                        type=argparse.FileType('rU'),
                        help='path of list of users to be added',
                        metavar='<users.txt>',
    )

    parser.add_argument('permission',
                        type=str,
                        help='permissions of each user to be added',
                        metavar='push|pull|admin',
    )

    parser.add_argument('-b', '--begin',
                        default=None,
                        help='only begin adding upon encountering this user',
                        metavar='<begin>',
    )


def add_collaborators(opt):
    g = Github(opt.githubToken())
    repo_full_name = f'{opt.owner}/{opt.repo}'
    repo = g.get_repo(repo_full_name)

    if not opt.promptYes((f'Are you sure you would like to add users from {opt.users.name} '
                            f'as collaborators to {repo_full_name} with {opt.permission} permissions?'), True):
        opt.warn('Aborting')
        return 

    opt.info(f'Proceeding to add {opt.users.name} as collaborators to {repo_full_name} with {opt.permission} permissions'

    do_add = opt.begin is None
    begin, added, total = 0, 0, 0
    for user in opt.users:
        try:
            user = user.strip()
            total = total + 1

            if not do_add and user == opt.begin:
                begin = total
                do_add = True

            if do_add:
                do_add_collaborator(repo, user, opt.permission, opt)
                added = added + 1
            else:
                opt.info(f'Skipped {user}')

        except Exception as e:
            opt.error(e)
            opt.error(f'{CMD_NAME} failed on {user} ({total})')
            return

    opt.info(f'Added {added} users of {total} total users, starting from index {begin}')


def main(args=None, config_path=None):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=add_collaborators_deco, req_github=True)

    add_collaborators(opt)


if __name__ == '__main__':
    main()
