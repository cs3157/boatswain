#!/usr/bin/env python3

import sys
import argparse
import csv
import requests
import canvaslib as cvl
import boatswain_env as benv
import logging
logging.setLevel(logging.INFO)

CMD_NAME = 'canvaswrangler'

def make_parser():
    parser = argparse.ArgumentParser(
            description='Upload grades and comments to Canvas')

    # grade options
    """
    parser.add_argument('-g', '--submit-grade',
                        default=False,
                        action='store_true',
                        help='upload grades',
    )
    """
    parser.add_argument('-G', '--grade-col',
                        default='grade',
                        type=str,
                        help='set name for grade header column',
                        metavar='<header>',
    )

    # comment options
    """
    parser.add_argument('-c', '--submit-comment',
                        default=False,
                        action='store_true',
                        help='upload comments',
    )
    """
    parser.add_argument('-C', '--comment-col',
                        default='comment',
                        type=str,
                        help='set name for comment header column',
                        metavar='<header>',
    )

    # student options
    parser.add_argument('-s', '--sdb',
                        default='sdb.csv',
                        type=argparse.FileType('rU'),
                        help='csv containing students\'s user-ids',
                        metavar='<sdb.csv>',
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

    # warning log options
    parser.add_argument('-L', '--log',
                        default='',
                        type=str,
                        help='set filename for warning log',
                        metavar='<warning.log>',
    )
    parser.add_argument('-N', '--no-log',
                        default=False,
                        action='store_true',
                        help='do not produce log file for warnings',
    )

    # testing options
    parser.add_argument('-n', '--noop',
                        default=False,
                        action='store_true',
                        help='do not submit grades; for testing purposes',
    )

    return parser


def retrieve_index(header_row, target):
    for i, cell in enumerate(header_row):
        if cell == target:
            return i
    return None


# TODO: make (comment & grade) index (grade | index)
# not necessary to have both
def retrieve_indices(header, uni_col, grade_col, comment_col):
    uni_idx = retrieve_index(header, uni_col)
    if uni_idx is None:
        raise IndexException('uni index not found')
    else:
        logging.info('uni index: %s', uni_idx)

    grade_idx = retrieve_index(header, grade_col)
    if grade_idx is None:
        raise IndexException('grade index not found')
    else:
        logging.info('grade index: %s', grade_idx)

    comment_idx = retrieve_index(header, opt.comment_idx)
    if comment_idx is None:
        raise IndexException('comment index not found')
    else:
        logging.info('comment index: %s', comment_idx)

    return uni_idx, grade_idx, comment_idx

def build_gradesheet(grades, sdb, uni_col, grade_col=None, comment_col=None):
    gradesheet = []
    for i, row in enumerate(grades):
        user_id = sdb[grades[uni_col]]

        if grade_col is not None:
            grade = row[grade_col]
        else:
            grade = None

        if comment_col is not None:
            comment = row[comment_col]
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

        Also feel free to contact jzh2106@columbia.edu about this error
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


# TODO: set noop to false
def wrangle_canvas(token, grades, sdb, opt):
    header = grades.next()

    uni_idx, grade_idx, comment_idx =
        retrieve_indices(header, opt.uni_col, opt.grade_col, opt.comment_col)

    gradesheet = build_gradesheet(grades, sdb, uni_idx, grade_idx, comment_idx)
    
    headers = cvl.auth_header(token)
    uri, data = cvl.update_grades(opt.course_id, opt.assignment_id, gradesheet)
    url = cvl.format_url(uri)

    if opt.noop:
        logging.info('--noop option specified; not submitting to Canvas.')
    else:
        return submit_grades(url, data, headers)


def main(argv=None, config_path=None, verbose=True):
    if argv is None:
        argv = sys.argv

    opt, config = benv.envParse(CMD_NAME, make_parser(), argv, config_path)

    grades = csv.reader(opt.grades)
    sdb = csv.reader(opt.sdb)

    res = wrangle_canvas(config.canvasToken(), grades, sdb, opt, noop=opt.noop)
    exit(res)
    
if __name__ == '__main__':
    main()
