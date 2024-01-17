#!/usr/bin/env python3

import sys
import pandas as pd
import boatswain_env as benv
import os

ROSTER_DIR = 'rosters/'

DESC = 'Create teams and handles csv files from original group form'
def clean_csv_deco(parser):
    parser.add_argument('csv_file',
                        type=str,
                        help='path to csv file containing original group form',
                        metavar='<csv_file>')
    
    parser.add_argument('hw',
                        type=str,
                        help='name of the hw in the following format hw<number>',
                        metavar='<hw>')


def produce_new_csv(opt):
    df = pd.read_csv(opt.csv_file)
    df = df.dropna(how='all')
    df["Group Name"] = df["Team #"].astype(int).astype(str) + "-" + df["Group Name"]

    df0 = df[["Group Name", "UNI", "GitHub Handle"]]
    df1 = df[["Group Name", "UNI.1", "GitHub Handle.1"]].rename(
        columns={"UNI.1": "UNI", "GitHub Handle.1": "GitHub Handle"})
    df2 = df[["Group Name", "UNI.2", "GitHub Handle.2"]].rename(
        columns={"UNI.2": "UNI", "GitHub Handle.2": "GitHub Handle"})

    union_dfs = pd.concat([df0, df1, df2]).dropna()



    union_dfs.to_csv(ROSTER_DIR + opt.hw + "-handles.csv", index=False)

    df_groups = df[
        ["Group Name", "GitHub Handle", "GitHub Handle.1", "GitHub Handle.2"]]

    df_groups.to_csv(ROSTER_DIR + opt.hw + "-teams.csv", index=False)

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    
    opt = benv.ParseOption(args, section=None, config_path=None, desc=DESC,
            parse_deco=clean_csv_deco)

    produce_new_csv(opt)

if __name__ == '__main__':
    main()
