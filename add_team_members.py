#!/usr/bin/env python3

import sys
from unittest.mock import MagicMock
import boatswain_env as benv
import argparse
from github import Github

CMD_NAME = 'add_team_members'
DESC = 'Add multiple users to a GitHub team'

def add_team_members_deco(parser):
    parser.add_argument('org',
                        type=str,
                        help='organization',
                        metavar='<org>',
    )

    parser.add_argument('team',
                        type=str,
                        help='team name',
                        metavar='<team>',
    )

    parser.add_argument('users',
                        type=argparse.FileType('rU'),
                        help='path of list of users to be added',
                        metavar='<users.txt>',
    )

    parser.add_argument('role',
                        type=str,
                        help='role of each user to be added',
                        metavar='member|maintainer',
    )

    parser.add_argument('-b', '--begin',
                        default=None,
                        help='only begin adding upon encountering this user',
                        metavar='<begin>',
    )

    parser.add_argument('-c', '--create',
                        default=False,
                        action='store_true',
                        help='create team first',
    )


def do_create_team(org, team_name, opt):
    opt.info(f'Creating secret team {team_name} in org {org.name}')

    if opt.noop:
        opt.log('--noop option specified; not creating team')
        mock_team = MagicMock()
        mock_team.name = team_name
        return mock_team

    team = org.create_team(team_name, privacy='secret')

    opt.info(f'Team {team.name} successfully created')

    return team


def do_add_team_member(team, user, role, opt):
    opt.info(f'Adding {user.login} as team member to {team.name} with {role} permissions')

    if opt.noop:
        opt.log('--noop option specified; not adding team member')
        return

    team.add_membership(user, role=role)

    opt.info(f'User {user.login} successfully added')


def add_team_members(opt):
    g = Github(opt.githubToken())
    org = g.get_organization(opt.org)

    team = None
    if opt.create:
        opt.info('--create option also specified; creating repo first')

        if not opt.promptYes('Are you sure you would like to proceed?', True):
            opt.warn('Aborting')
            return

        team = do_create_team(org, opt.team, opt)
    else:
        for t in org.get_teams():
            if t.name == opt.team:
                team = t
                break

    if team is None:
        opt.error(f'Team {opt.team} not found in org {opt.org}')
        opt.error('You may try passing the --create flag to create it')
        return

    opt.info(f'Adding users from {opt.users.name} as team members to {org.name}/{team.name} with {opt.role} permissions')

    if not opt.promptYes('Are you sure you would like to proceed?', True):
        opt.warn('Aborting')
        return

    do_add = opt.begin is None
    begin, added, total = 0, 0, 0
    for user in opt.users:
        try:
            user = user.strip()
            total = total + 1

            if not do_add and user == opt.begin:
                begin = total
                do_add = True

            if do_add:
                do_add_team_member(team, g.get_user(user), opt.role, opt)
                added = added + 1
            else:
                opt.info('Skipped {}'.format(user))

        except Exception as e:
            opt.error(e)
            opt.error('{} failed on {} ({})'.format(CMD_NAME, user, total))
            return

    opt.info('Added {} users of {} total users, starting from index {}'
            .format(added, total, begin))


def main(args=None, config_path=None):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=add_team_members_deco, req_github=True)

    add_team_members(opt)


if __name__ == '__main__':
    main()
