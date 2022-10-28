import sys

from canvasapi import Canvas

import boatswain_env as benv


def wrangler_deco(parser):
    parser.add_argument('course_id',
                        type=str,
                        help='course-id from Canvas',
                        metavar='<course-id>',
    )
    parser.add_argument('assignment_name',
                        type=str,
                        help='assignment-name',
                        metavar='<assignment-name>',
    )
    parser.add_argument('points',
                        type=int,
                        help='points',
                        metavar='<points>',
    )


def create_assignment(opt):
    canvas = Canvas(opt.config.canvasUrl(), opt.config.canvasToken())
    course = canvas.get_course(opt.course_id)

    # note: create_assignment() cannot set post_manually, bc canvas is silly
    new_assignment = course.create_assignment({
        'name': opt.assignment_name,
        'submission_types': [],
        'notify_of_update': False,
        'points_possible': opt.points,
        'grading_type': 'points',
        'description': '',
        'published': True
    })

    return new_assignment


def main(args=None, config_path=None):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, parse_deco=wrangler_deco, config_path=config_path)

    new_assignment = create_assignment(opt)
    print(new_assignment.id)


if __name__ == '__main__':
    main()

