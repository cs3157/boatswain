#!/usr/bin/env python3

import sys
import boatswain_env as benv
import argparse
import csv 
import os
from github import Github

CMD_NAME = 'drop_students'
DESC = 'Remove dropped students from GitHub team repo'

def drop_students_deco(parser):
    parser.add_argument('org',
                    type=str,
                    help='organization name',
                    metavar='<org>',
    )
    parser.add_argument('roster',
                    type=str,
                    help='roster CSV file',
                    nargs='?',
                    default='',
                    metavar='<roster.csv>')

    parser.add_argument('github_handles',
                    type=str,
                    help='matches uni to github handle CSV file',
                    nargs='?',
                    default='',
                    metavar='<uni_to_github.csv>')

    args = parser.parse_args()

    if args.roster == '' or args.github_handles == '':
        parser.print_usage()
        print(f"{parser.prog}: error: too few arguments")
        exit()

def find_and_drop_students(opt):
    with open(opt.roster) as r:
        roster = csv.DictReader(r)
        roster_l = [x['SIS Login ID'] for x in roster]

        with open(opt.github_handles) as g:
            handles = csv.DictReader(g)

            for row in handles:
                if row['UNI'] not in roster_l:
                    remove_collaborator(row['GitHub Handle'], opt)
                    

def remove_collaborator(handle, opt):
    g = Github(opt.githubToken())
    org = g.get_organization(opt.org)
    user = g.get_user(handle)

    if not opt.promptYes(('Are you sure you would like to remove {} '
                            'as a member of {}?')
                            .format(handle, org),
                        True):
        opt.warn('Aborting')
        return
    try:
        do_remove_collaborator(org, user, opt)
    except Exception as e:
        opt.error(e)
        opt.error('{} failed on {}'.format(CMD_NAME, user))
        return

def do_remove_collaborator(org, user, opt):
        org.remove_from_members(user)
    

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=None, config_path=None,
            desc=DESC, parse_deco=drop_students_deco, req_github=True)

    find_and_drop_students(opt)

if __name__ == '__main__':
    main()