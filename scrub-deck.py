#!/usr/bin/env python3

import sys
import re
import boatswain_env as benv
from github import Github


CMD_NAME = 'scrub'
DESC = 'Delete all repos from a GitHub org'


def scrub_deco(parser):
    parser.add_argument('-f', '--filter',
                        default=r'.*',
                        type=re.compile,
                        help='only scrub repos matching regular expression',
                        metavar='<regex>',
    )

    parser.add_argument('-i', '--invert',
                        action='store_true',
                        help='invert regex filter',
    )

    parser.add_argument('org_name',
                        type=str,
                        help='organization to be scrubbed',
                        metavar='<org-name>',
    )


def do_scrub(repo, opt):
    if opt.noop:
        opt.log(f'--noop option specified; not deleting {repo.name}')
        return

    opt.warn(f'Deleting {repo.name}...')
    repo.delete()


def scrub_org(opt):
    g = Github(opt.githubToken())
    org = g.get_organization(opt.org_name)

    opt.warn(f'Scrubbing Github Org: {org.login} ({org.url})')

    if not opt.promptYes('Are you sure you want to scrub this org?', False):
        # deliberately disallow --yes to work
        opt.info('Backing out of scrub because user was indecisive')
        return

    if not opt.promptYes('You realize this means every repo in this org will be'
            ' removed, right?', True):
        opt.info('Backing out of scrub because confused user needs a moment')
        return
    for repo in org.get_repos():
        repo_name = repo.full_name.split('/')[-1]
        if opt.invert:
            if opt.filter.fullmatch(repo_name):
                opt.info(f'Skipping {repo_name}; matched with inverted filter: {opt.filter}')
                continue
        else:
            if not opt.filter.fullmatch(repo_name):
                opt.info(f'Skipping {repo_name}; did not match with filter: {opt.filter}')
                continue

        do_scrub(repo, opt)

    opt.warn('Double-check all repos have actually been removed.')
    opt.warn('Sometimes you need to re-run this a couple of times.')


def main(args=None, config_path=None, verbose=True):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=scrub_deco, req_github=True)

    scrub_org(opt)


if __name__ == '__main__':
    main()
