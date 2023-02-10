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
    parser.add_argument('owner',
                    type=str,
                    help='repo owner (individual or organization)',
                    metavar='<repo-owner>',
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
                    remove_collaborator(row['GitHub Handle'], row['Group Name'],opt)
                    

def remove_collaborator(handle, group_name, opt):
    g = Github(opt.githubToken())
    org = g.get_organization(opt.owner)
    print(org)
    #repo_full_name = '{}/{}'.format(opt.owner, group_name)
    #repo = g.get_repo(repo_full_name)
    #user = g.get_user(handle)

    if not opt.promptYes(('Are you sure you would like to remove {} '
                            'as a member of {}?')
                            .format(handle, org),
                        True):
        opt.warn('Aborting')
        return
    user = g.get_user(handle)
    do_remove_collaborator(org, user, opt)

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