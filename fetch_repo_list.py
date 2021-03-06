#!/usr/bin/env python3

import sys
import boatswain_env as benv
import argparse
import csv
from github import Github

CMD_NAME = 'fetch_repo_list'
DESC = 'Fetch a list of all repos under an org'

def fetch_repo_list_deco(parser):
    parser.add_argument('org',
                        type=str,
                        help='repo owner organization',
                        metavar='<org>',
    )

def fetch_repo_list(opt):
    g = Github(opt.githubToken())
    org = g.get_organization(opt.org)

    for repo in org.get_repos(type='all'):
        print(f"{opt.org}/{repo.name}")

def main(args=None, config_path=None):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=fetch_repo_list_deco, req_github=True)

    fetch_repo_list(opt)


if __name__ == '__main__':
    main()
