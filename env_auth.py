#!/usr/bin/env python3

import os

GITHUB_DEFAULT_PATH = os.path.expanduser('~/.github.auth')
CANVAS_DEFAULT_PATH = os.path.expanduser('~/.canvas.auth')

def read_token_file(filename):
    with open(os.path.expanduser(filename)) as f:
        t = f.read()
        if t is None:
            return None
        return t.rstrip()

def main():
    try:
        github_tok = read_token_file(GITHUB_DEFAULT_PATH)
    except FileNotFoundError:
        github_tok = None

    if github_tok is None:
        print('GitHub token not found at {}'.format(GITHUB_DEFAULT_PATH))
    else:
        print('GitHub token = {}'.format(github_tok))


    try:
        canvas_tok = read_token_file(CANVAS_DEFAULT_PATH)
    except FileNotFoundError:
        canvas_tok = None
    if canvas_tok is None:
        print('Canvas token not found at {}'.format(CANVAS_DEFAULT_PATH))
    else:
        print('Canvas token = {}'.format(canvas_tok))

if __name__ == '__main__':
    main()
