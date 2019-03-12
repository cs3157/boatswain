#!/usr/bin/env python3

import sys
import argparse
import csv
import requests
import canvaslib as cvl
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
                        type=argparse.FileType('rU'),
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


def build_gradesheet(grades, student_idx, grade_idx=None, comment_idx=None):
    gradesheet = []
    for i, row in enumerate(grades):
        user_id = row[student_idx]

        if grade_idx is not None:
            grade = row[grade_idx]
        else:
            grade = None

        if comment_idx is not None:
            comment = row[comment_idx]
        else:
            comment = None
        gradesheet.append(cvl.GradesheetEntry(user_id, grade, comment))

    return gradesheet


def log_post_success(res, opt):
    opt.info('Course ID: {}', res['context_id'])
    opt.info('Assignment ID: {}', res['id'])
    opt.info('''
        Please wait as Canvas processes this POST request...
        Feel free to check its progress at:
            {}
        ''', res['url'])


def log_post_error(res, opt):
    opt.error('Error report ID: {}', res['error_report_id'])
    for error in res['errors']:
        opt.error('Error message: {}', error['message'])
    opt.error('''
        If that wasn\'t helpful (which it usually isn\'t),
        please try the following:
          - Make sure the assignment is published
          - Sanitize unsupported unicode characters
            (most commmonly smart quotations)
          - Try again later; this might be a server error
          - Try turning your computer off and on again
            ^^^please don't actually

        Also please contact jzh2106@columbia.edu (maintainer) about this error
    ''')


def submit_grades(url, data, headers, opt):
    response = requests.post(url, data=data, headers=headers)
    res = response.json()

    if response.status_code == requests.codes.ok:
        opt.log('Grades and comments successfully submitted')
        log_post_success(res, opt)
    else:
        opt.error('Error: {}', response.status_code)
        log_post_error(res, opt)
    return response.status_code


def log_dump_wrangler(url, data, headers, opt):
    opt.info('API URL: {}'.format(url))
    opt.info('Headers: {}'.format(headers))
    opt.info('Data: {')
    for k in data:
        opt.info('{} : {}'.format(k, data[k]))
    opt.info('}')
    opt.info('')

def wrangle_canvas(opt):
    grades = csv.reader(opt.grades)
    header = next(grades)

    student_idx, grade_idx, comment_idx = retrieve_indices(header, opt)

    gradesheet = build_gradesheet(grades, student_idx, grade_idx, comment_idx)
    
    headers = cvl.auth_header(opt.canvasToken())
    uri, data = cvl.update_grades(opt.course_id, opt.assignment_id, gradesheet)
    url = cvl.format_url(uri)

    log_dump_wrangler(url, data, headers, opt)

    opt.log('About to submit. Make sure the assignment is muted.')
    cont = opt.promptYes('Would you like to continue?', True)

    if not cont:
        opt.log('Aborting; not submitting to Canvas')
        return

    if opt.noop:
        opt.log('--noop option specified; not submitting to Canvas')
        return

    opt.log('Submitting to Canvas...')
    return submit_grades(url, data, headers, opt)


def main(args=None, config_path=None, verbose=True):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=wrangler_deco, req_canvas=True)

    res = wrangle_canvas(opt)
    exit(res)
    
if __name__ == '__main__':
    main()
