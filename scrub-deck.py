#!/usr/bin/env python3

import sys
import boatswain_env as benv
from github import Github

CMD_NAME = 'scrub'
DESC = 'Delete all repos from a GitHub org'

def scrub_deco(parser):
    parser.add_argument('org_name',
                        type=str,
                        help='organization to be scrubbed',
                        metavar='<org-name>',
    )


def scrub(repo, opt):
    print(repo)
    # repo.delete()


def scrub_org(opt):
    g = Github(opt.githubToken())
    org = g.get_organization(opt.org_name)

    opt.warn('Scrubbing Github Org: {} ({})'.format(org.login, org.url))

    if not opt.promptYes('Are you sure you want to scrub this org?', False):
        # deliberately disallow --yes to work
        opt.info('Backing out of scrub because user was indecisive')
        return

    if not opt.promptYes('You realize this means every repo in this org will be'
            ' removed, right?', True):
        opt.info('Backing out of scrub because confused user needs a moment')
        return

    for repo in org.get_repos():
        scrub(repo, opt)


def main(args=None, config_path=None, verbose=True):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=scrub_deco, req_github=True)

    scrub_org(opt)


if __name__ == '__main__':
    main()
