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


def add_collaborator(opt):
    g = Github(opt.githubToken())
    repo_full_name = '{}/{}'.format(opt.owner, opt.repo)


    print(repo_full_name)
    repo = g.get_repo(repo_full_name)

    if not opt.promptYes(('Are you sure you would like to add {} '
                            'as a collaborator to {} with {} permissions?')
                            .format(opt.user, repo_full_name, opt.permission),
                        True):
        opt.warn('Aborting')
        return 

    opt.info('Proceeding to {} as collaborator to {} with {} permissions'
            .format(opt.user, repo_full_name, opt.permission))

    repo.add_to_collaborators(opt.user, permission=opt.permission)

    opt.info('User {} successfully added'.format(opt.user))

def main(args=None, config_path=None):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=add_collaborator_deco, req_github=True)

    add_collaborator(opt)


if __name__ == '__main__':
    main()
