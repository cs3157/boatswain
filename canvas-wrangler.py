#!/usr/bin/env python3

import sys
import argparse
import csv
import requests
import canvaslib as cvl
import logging
import boatswain_env as benv

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
    parser.add_argument('-n', '--no-submit',
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


# TODO: set noop to false
def wrangle_canvas(token, grades, sdb, opt, noop=True):
    header = grades.next()

    uni_col = retrieve_index(header, opt.uni_col)
    grade_col = retrieve_index(header, opt.grade_col)
    comment_col = retrieve_index(header, opt.comment_col)

    # bad error checking now
    if uni_col is None or grade_col is None or comment_col is None:
        logging.error('{} {} {}'.format(uni_col, grade_col, comment_col))
        return
    
    gradesheet = build_gradesheet(grades, sdb, uni_col, grade_col, comment_col)
    
    headers = auth_header(token)
    uri, data = cvl.update_grades(opt.course_id, opt.assignment_id, gradesheet)
    url = format_url(uri)

    if not noop:
        print("lol")
        return
        res = requests.post(url, data=data, headers=headers)


def main(argv=None, config_path=None, verbose=True):
    if argv is None:
        argv = sys.argv

    opt, config = benv.envParse(CMD_NAME, make_parser(), argv, config_path)

    grades = csv.reader(opt.grades)
    sdb = csv.reader(opt.sdb)

    wrangle_canvas(config.canvasToken(), grades, sdb, opt, noop=opt.noop)
    
if __name__ == '__main__':
    main()
