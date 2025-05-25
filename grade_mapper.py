#!/usr/bin/env python3
"""
Grade Mapping and Statistics Tool

Usage:
------
1. Mapping grader output to CourseWorks CSV format:
   python3 grade_mapper.py map -u path/to/uni_map.csv -g path/to/grader_output.csv [-o path/to/output.csv] [-v]

2. Computing statistics from the mapped grade file:
   python3 grade_mapper.py stats -m path/to/output.csv

Arguments:
----------
-u, --uni-map: CSV file mapping team names to UNIs (first row is header)
    Example:
        Team Number,Teammate 1,Teammate 2,Teammate 3
        team1-AAA,aa1111,bb2222,cc3333
        team3-BBB,yy1111,zz2222,
-g, --grader-output: Pygrader raw output in semi-CSV format (comma-delimited, comments may contain commas)
    Example:
        team1-AAA,150,(A3); (D1.2) xxxx; (E1.4) xxxx;
        team3-BBB,155,(B1.3) xxxx; (D1.2) xxxx; (E1.2); (E1.4); (E2.5); (E2.7)
-o, --output: Output CSV file with header 'uni, grade, comment'. If not given, prints to stdout.
-m, --mapped-grades: A mapped CSV file to compute statistics on.
-v, --verify: (optional) If set, will enable the verifier to report unmatched team names from either input

Author: Alex Jiakai Xu
"""

import argparse
import csv
import sys
import statistics
from dataclasses import dataclass
from typing import List, Dict, Optional, Set

@dataclass
class GradeRecord:
    identifier: str
    grade: float
    comment: str

def read_uni_mapping(uni_map_path: str) -> Dict[str, List[str]]:
    mapping = {}
    with open(uni_map_path, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            team = row[0]
            unis = [u for u in row[1:4] if u]
            mapping[team] = unis
    return mapping

def read_grader_output(grader_path: str) -> List[GradeRecord]:
    grades = []
    with open(grader_path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            team, grade, comment = row[0], float(row[1]), ','.join(row[2:]).strip()
            grades.append(GradeRecord(identifier=team, grade=grade, comment=comment))
    return grades

def map_to_student_grades(team_grades: List[GradeRecord], mapping: Dict[str, List[str]], report_missing: bool = False) -> List[GradeRecord]:
    student_grades = []
    graded_teams = set()
    verifier_flag = False

    for tg in team_grades:
        graded_teams.add(tg.identifier)
        unis = mapping.get(tg.identifier)
        if unis is None:
            if report_missing:
                print(f"Verifier >> Warning: Team '{tg.identifier}' not found in uni map.", file=sys.stderr)
            verifier_flag = True
            continue
        for uni in unis:
            student_grades.append(GradeRecord(identifier=uni, grade=tg.grade, comment=tg.comment))

    if report_missing:
        unmapped_teams = set(mapping.keys()) - graded_teams
        for team in sorted(unmapped_teams):
            print(f"Verifier >> Notice: Team '{team}' in uni map not found in grader output.", file=sys.stderr)
            verifier_flag = True

    if report_missing and verifier_flag:
        print("Verifier >> Notice: Some teams were not mapped. Please check the input files.", file=sys.stderr)
    elif report_missing and not verifier_flag:
        print("Verifier >> All teams were successfully mapped.", file=sys.stderr)

    return student_grades

def write_student_grades(student_grades: List[GradeRecord], output_path: Optional[str] = None):
    lines = ["uni,grade,comment"]
    for sg in student_grades:
        grade_out = int(sg.grade) if sg.grade.is_integer() else round(sg.grade, 2)
        comment_out = sg.comment.replace('"', '""')  # Escape quotes
        lines.append(f"{sg.identifier},{grade_out},\"{comment_out}\"")

    if output_path:
        with open(output_path, 'w', newline='') as f:
            f.write('\n'.join(lines) + '\n')
    else:
        print('\n'.join(lines))

def compute_statistics(grades: List[float], label: str):
    filtered = [g for g in grades if g > 0]
    if not filtered:
        print(f"No non-zero grades for {label}.")
        return
    print(f"Statistics for {label} (non-zero grades only):")
    print(f"  Count: {len(filtered)}")
    print(f"  Mean: {statistics.mean(filtered):.2f}")
    print(f"  Median: {statistics.median(filtered):.2f}")
    print(f"  Std Dev: {statistics.stdev(filtered):.2f}" if len(filtered) > 1 else "  Std Dev: N/A")
    print(f"  Max: {max(filtered):.2f}\n")

def command_map(args):
    mapping = read_uni_mapping(args.uni_map)
    team_grades = read_grader_output(args.grader_output)
    student_grades = map_to_student_grades(team_grades, mapping, report_missing=args.verify)
    write_student_grades(student_grades, args.output)
    # Compute statistics
    compute_statistics([tg.grade for tg in team_grades], label='Teams')
    compute_statistics([sg.grade for sg in student_grades], label='Students')

def command_stats(args):
    grades = []
    with open(args.mapped_grades, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            grades.append(float(row['grade']))
    compute_statistics(grades, label='Students')

def main():
    parser = argparse.ArgumentParser(description="Process and analyze grades for Courseworks upload.")
    subparsers = parser.add_subparsers(dest='command')

    # Mapping command
    parser_map = subparsers.add_parser('map', help='Map grader output to student UNIs')
    parser_map.add_argument('-u', '--uni-map', required=True, help='CSV file mapping team names to UNIs')
    parser_map.add_argument('-g', '--grader-output', required=True, help='Grader output CSV')
    parser_map.add_argument('-o', '--output', help='Output CSV file for CourseWorks upload')
    parser_map.add_argument('-v', '--verify', action='store_true', help='Report unmapped team names in either input')

    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Compute stats from mapped CSV')
    parser_stats.add_argument('-m', '--mapped-grades', required=True, help='Mapped CSV file with uni,grade,comment')

    args = parser.parse_args()

    if args.command == 'map':
        command_map(args)
    elif args.command == 'stats':
        command_stats(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
