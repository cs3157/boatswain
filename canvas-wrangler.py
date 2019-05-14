#!/usr/bin/env python3

import sys
import argparse
import csv
from canvasapi import Canvas
import boatswain_env as benv

CMD_NAME = 'canvaswrangler'
DESC = 'Upload grades and comments to Canvas'

def wrangler_deco(parser):
    parser.add_argument('-G', '--grade-col',
                        default='grade',
                        type=str,
                        help='set name for grade header column, '
                            'pass empty string to not submit grades',
                        metavar='<header>',
    )

    parser.add_argument('-C', '--comment-col',
                        default='comment',
                        type=str,
                        help='set name for comment header column, '
                            'pass empty string to not submit comment',
                        metavar='<header>',
    )

    parser.add_argument('-S', '--student-col',
                        default='uni',
                        type=str,
                        help='set name for student header column',
                        metavar='<header>',
    )

    # required positional args
    parser.add_argument('course_id',
                        type=str,
                        help='course-id from Canvas',
                        metavar='<course-id>',
    )
    parser.add_argument('assignment_id',
                        type=str,
                        help='assignment-id from Canvas',
                        metavar='<assignment-id>',
    )
    parser.add_argument('grades',
                        type=argparse.FileType('r'),
                        help='csv containing grades and/or comments',
                        metavar='<grades.csv>',
    )


def retrieve_index(header_row, target):
    for i, cell in enumerate(header_row):
        if cell == target:
            return i
    raise LookupError('{} index not found'.format(target))


def retrieve_indices(header, opt):
    if opt.student_col == '':
        raise LookupError('must specify student column header value')
    else:
        student_idx = retrieve_index(header, opt.student_col)
        opt.info('student index: {}', student_idx)

    if opt.grade_col == '' and opt.comment_col == '':
        raise LookupError('neither grade nor column specified')

    if opt.grade_col == '':
        grade_idx = None
        opt.info('empty grade column specified, not submitting grades')
    else:
        grade_idx = retrieve_index(header, opt.grade_col)
        opt.info('grade index: {}', grade_idx)

    if opt.comment_col == '':
        comment_idx = None
        opt.info('empty comment column specified, not submitting comments')
    else:
        comment_idx = retrieve_index(header, opt.comment_col)
        opt.info('comment index: {}', comment_idx)

    return student_idx, grade_idx, comment_idx


def build_grade_data(grades, student_i, grade_i, comment_i, opt):
    grade_data = {}
    for i, row in enumerate(grades):
        grade_entry = {}
        user_id = row[student_i]

        if grade_i is not None:
            grade = row[grade_i]
            grade_entry['posted_grade'] = grade
        else:
            grade = None

        if comment_i is not None:
            comment = row[comment_i]
            grade_entry['text_comment'] = comment
        else:
            comment = None

        opt.info('{} ({}): {}'.format(user_id, grade, comment))
        grade_data['sis_user_id:{}'.format(user_id)] = grade_entry

    return grade_data


def log_dump_wrangler(grade_data, course, assignment, opt):
    opt.info('Course: {}'.format(course))
    opt.info('Assignment: {}'.format(assignment))
    opt.info('Grade Data: {')
    for k in grade_data:
        opt.info('{} : {}'.format(k, grade_data[k]))
    opt.info('}')
    opt.info('')

def submit_grades(grade_data, assignment, opt):
    opt.log('About to submit. Make sure the assignment is muted.')
    cont = opt.promptYes('Would you like to continue?', True)

    if not cont:
        opt.log('Aborting; not submitting to Canvas')
        return

    if opt.noop:
        opt.log('--noop option specified; not submitting to Canvas')
        return

    opt.log('Submitting to Canvas...')
    return assignment.submissions_bulk_update(grade_data=grade_data)

def wrangle_canvas(opt):
    grades = csv.reader(opt.grades)
    header = next(grades)

    student_i, grade_i, comment_i = retrieve_indices(header, opt)

    grade_data = build_grade_data(grades, student_i, grade_i, comment_i, opt)

    canvas = Canvas(opt.canvasUrl(), opt.canvasToken())
    course = canvas.get_course(opt.course_id)
    assignment = course.get_assignment(opt.assignment_id)

    progress = submit_grades(grade_data, assignment, opt)

    # do something with progress? it has the following useful fields:
    #   .workflow_state = 'completed' | 'running' | *
    #   .query()        // checks progress
    #   .tag            // what the progress is for
    #   .message        // tells you how many courses updated
    # we can have the option to block until complete


def main(args=None, config_path=None, verbose=True):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=wrangler_deco, req_canvas=True)

    wrangle_canvas(opt)

if __name__ == '__main__':
    main()
