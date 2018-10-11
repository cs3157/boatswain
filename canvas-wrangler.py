#!/usr/bin/env python3

import sys
import argparse
import csv
import requests
import canvaslib as cvl
import boatswain_env as benv
import logging

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
                            'pass empty string to not submit grades',
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
    raise LookupError('uni index not found')


def retrieve_indices(header, student_col, grade_col, comment_col):
    if student_col == '':
        raise LookupError('must specify student column header value')
    else:
        student_idx = retrieve_index(header, student_col)
        logging.debug('student index: %s', student_idx)

    if grade_col == '' and comment_col == '':
        raise LookupError('neither grade nor column specified')

    if grade_col == '':
        grade_idx = None
        logging.debug('empty grade column specified, not submitting grades')
    else:
        grade_idx = retrieve_index(header, grade_col)
        logging.debug('grade index: %s', grade_idx)

    if comment_col == '':
        comment_idx = None
        logging.debug('empty comment column specified, not submitting comments')
    else:
        comment_idx = retrieve_index(header, comment_col)
        logging.debug('comment index: %s', comment_idx)

    logging.debug('')

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


def log_post_success(res):
    logging.info('Course ID: %s', res['context_id'])
    logging.info('Assignment ID: %s', res['id'])
    logging.info('''
        Please wait as Canvas processes this POST request...
        Feel free to check its progress at:
            %s
        ''', res['url'])


def log_post_error(res):
    logging.error('Error report ID: %s', res['error_report_id'])
    for error in res['errors']:
        logging.error('Error message: %s', error['message'])
    logging.error('Error code: %s', error['error_code'])
    logging.error('''
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


def submit_grades(url, data, headers):
    response = requests.post(url, data=data, headers=headers)
    res = response.json()

    if response.status_code == requests.codes.ok:
        logging.info('Grades and comments successfully submitted')
        log_post_success(res)
    else:
        logging.error('Error:', response.status_code)
        log_post_error(res)
    return response.status_code


def log_dump_wrangler(url, data, headers, opt):
    if opt.verbose:
        logging.debug('API URL: {}'.format(url))
        logging.debug('Headers: {}'.format(headers))
        logging.debug('Data: {')
        for k in data:
            logging.debug('\t{} : {}'.format(k, data[k]))
        logging.debug('}')
        logging.debug('')

def wrangle_canvas(opt):
    grades = csv.reader(opt.grades)
    header = next(grades)

    student_idx, grade_idx, comment_idx = retrieve_indices(
            header, opt.student_col, opt.grade_col, opt.comment_col)

    gradesheet = build_gradesheet(grades, student_idx, grade_idx, comment_idx)
    
    headers = cvl.auth_header(opt.canvasToken())
    uri, data = cvl.update_grades(opt.course_id, opt.assignment_id, gradesheet)
    url = cvl.format_url(uri)

    log_dump_wrangler(url, data, headers, opt)

    if opt.noop:
        logging.info('--noop option specified; not submitting to Canvas.')
    else:
        return submit_grades(url, data, headers)


def main(args=None, config_path=None, verbose=True):
    if args is None:
        args = sys.argv[1:]

    opt = benv.ParseOption(args, section=CMD_NAME, config_path=config_path,
            desc=DESC, parse_deco=wrangler_deco, req_canvas=True)

    if opt.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    res = wrangle_canvas(opt)
    exit(res)
    
if __name__ == '__main__':
    main()
