#!/usr/bin/env python3

import sys
import boatswain_env as benv
from github import Github
from add_collaborator import add_collaborator_repo

CMD_NAME = 'add_collaborators'
DESC = 'Add multiple users as collaborator to GitHub repo'

def mk_repo_deco(parser):
    parser.add_argument('org',
                        type=str,
                        help='organization name',
                        metavar='<org>',
    )

    parser.add_argument('prefix',
                        type=str,
                        help='prefix prepended to each repo',
                        metavar='<prefix>',
    )

    parser.add_argument('repo',
                        type=str,
                        help='repo name, appended to prefix',
                        metavar='<repo>',
    )


def fmt_hyphen(prefix, name):
    if prefix[-1] == '-':
        return '{}{}'.format(prefix, name)
    else:
        return '{}-{}'.format(prefix, name)


def do_mk_repo(org, repo_name, opt):
    opt.info('creating private repo {} under organization {}'.format(repo_name, org))
    
    repo = org.create_repo(repo_name, private=True)

    # funky output so easily greppable
    opt.warn('@CREATED_REPO: {} {}'.format(repo_name, repo.git_url))

    return repo


def mk_repo(opt):
    g = Github(opt.githubToken())
    org = g.get_organization(opt.org)

    repo_name = fmt_hyphen(opt.prefix, opt.repo)

    if not opt.promptYes(('Are you sure you would like to create a private '
                            'repo under organization {} named {}?')
                            .format(opt.org, repo_name),
                            True):
        opt.warn('Aborting')
        return 

    opt.info('Proceeding to create private repo {}/{}'
            .format(opt.org, repo_name))

    do_mk_repo(org, repo_name, opt)


def main(args=None, config_path=None):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=mk_repo_deco, req_github=True)

    mk_repo(opt)


if __name__ == '__main__':
    main()
