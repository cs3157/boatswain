#!/usr/bin/env python3

import sys
import boatswain_env as benv
from github import Github
from add_collaborator import add_collaborator_repo

CMD_NAME = 'add_collaborators'
DESC = 'Add multiple users as collaborator to GitHub repo'

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

    parser.add_argument('path',
                        type=str,
                        help='path of list of users to be added',
                        metavar='<path>',
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
    repo_full_name = '{}/{}'.format(opt.owner, opt.repo)
    repo = g.get_repo(repo_full_name)

    if not opt.promptYes(('Are you sure you would like to add users from {} '
                            'as collaborators to {} with {} permissions?')
                            .format(opt.path, repo_full_name, opt.permission),
                        True):
        opt.warn('Aborting')
        return 

    opt.info('Proceeding to add {} as collaborators to {} with {} permissions'
            .format(opt.path, repo_full_name, opt.permission))

    with open(opt.path) as users:
        do_add = opt.begin is None
        begin, added, total = 0, 0, 0
        for user in users:
            try:
                user = user.strip()
                total = total + 1

                if not do_add and user == opt.begin:
                    begin = total
                    do_add = True

                if do_add:
                    add_collaborator_repo(repo, user, opt.permission, opt)
                    added = added + 1
                else:
                    opt.info('Skipped {}'.format(user))

            except Exception as e:
                opt.error(e)
                opt.error('{} failed on {}'.format(CMD_NAME, user))
                return

    opt.info('Added {} users of {} total users, starting from index {}'
            .format(added, total, begin))


def main(args=None, config_path=None):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=add_collaborator_deco, req_github=True)

    add_collaborators(opt)


if __name__ == '__main__':
    main()
