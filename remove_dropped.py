#!/usr/bin/env python3

import sys
import boatswain_env as benv
import argparse
import csv 
import os
from github import Github

parser = argparse.ArgumentParser(
    description='Remove dropped students from Github Team Org')

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

if args.roster == '':
    parser.print_usage()
    print(f"{parser.prog}: error: too few arguments")
    exit()

with open(args.roster) as r:
    roster = csv.DictReader(r)
    roster_l = [x['SIS Login ID'] for x in roster]

    with open(args.github_handles) as g:
        handles = csv.DictReader(g)

        for row in handles:
            if row['UNI'] not in roster_l:
                print(row['UNI'])


