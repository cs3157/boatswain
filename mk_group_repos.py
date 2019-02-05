#!/usr/bin/env python3

import sys
import boatswain_env as benv
import argparse
import csv
from github import Github

from add_collaborator import add_collaborator_repo
from mk_repo import do_mk_repo, fmt_hyphen

CMD_NAME = 'mk_group_repos'
DESC = 'Make repos for groups'

def mk_group_repos_deco(parser):
    parser.add_argument('org',
                        type=str,
                        help='repo owner organization',
                        metavar='<org>',
    )

    parser.add_argument('prefix',
                        type=str,
                        help='prefix prepended to each repo',
                        metavar='<prefix>',
    )

    parser.add_argument('groups',
                        type=argparse.FileType('rU'),
                        help='path of list of groups (group,[member,])',
                        metavar='<groups.csv>',
    )

    parser.add_argument('permission',
                        type=str,
                        help='permissions of each user to be added',
                        metavar='push|pull|admin',
    )

    parser.add_argument('-l', '--lookup',
                        default=False,
                        action='store_true',
                        help='look up existing repo rather than create one',
    )

    # hopefully we won't need this
    # parser.add_argument('-b', '--begin',
    #                     default=None,
    #                     help='only begin adding upon encountering this user',
    #                     metavar='<begin>',
    # )


def mk_group_repos(opt):
    g = Github(opt.githubToken())
    org = g.get_organization(opt.org)

    if not opt.promptYes(('Are you sure you would like to create group repos for '
                            'users in {} under organization {} with name {}')
                            .format(opt.groups.name, opt.org,
                                fmt_hyphen(opt.prefix, '<group>')),
                        True):
        opt.warn('Aborting')
        return 

    opt.info('Creating repos under {} for groups in {}, with name {}'
            .format(opt.groups.name, opt.org,
                fmt_hyphen(opt.prefix, '<group>')))

    for g in csv.reader(opt.groups):
        group, members = g[0], [m.strip() for m in g[1:] if m != '']

        repo_name = fmt_hyphen(opt.prefix, group)

        if opt.lookup:
            opt.info('Looking up repo {}/{}'.format(org.name, repo_name))
            repo = org.get_repo(repo_name)
        else:
            repo = do_mk_repo(org, repo_name, opt)

        opt.info('Adding {} to {}'.format(members, repo.full_name))
        for member in members:
            add_collaborator_repo(repo, member, opt.permission, opt)


def main(args=None, config_path=None):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=mk_group_repos_deco, req_github=True)

    mk_group_repos(opt)


if __name__ == '__main__':
    main()
