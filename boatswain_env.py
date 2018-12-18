#!/usr/bin/env python

import configparser
import os
import argparse

import interactive as itv

DEFAULT_INI_PATH = os.path.expanduser('~/.boatswain.ini')

CANVAS_SECTION = 'canvas'
CANVAS_TOKEN = 'token'

GITHUB_SECTION = 'github'
GITHUB_TOKEN = 'token'

DEBUG, DEBUG_TAG    = 30,   'DEBUG'
INFO, INFO_TAG      = 20,   'INFO'
WARN, WARN_TAG      = 10,   'WARN'  # default
ERROR, ERROR_TAG    = 0,    'ERROR'
SILENT              = -1


'''
Represents CSV configuration file
'''
class BoatswainConfig(configparser.ConfigParser):
    def __init__(self, path=DEFAULT_INI_PATH):
        super().__init__()
        self.path = path
        self.read(path)

    def canvasToken(self):
        return self.get(CANVAS_SECTION, CANVAS_TOKEN)

    def githubToken(self):
        return self.get(GITHUB_SECTION, GITHUB_TOKEN)

def _fmt(fmt, *args, tag=None):
    return fmt

# No __init__ function. ParseOption is its factory that uses argparse
class BoatswainOption(argparse.Namespace):
    '''
    If tokens were set by arg parse stage, then just return that.
    Otherwise, read it in from config, and possibly fail if it's not there
    '''
    def canvasToken(self):
        if self.canvas_token is None:
            return self.config.canvasToken()
        return self.canvas_token

    def githubToken(self):
        if self.github_token is None:
            return self.config.githubToken()
        return self.github_token

    def log(self, fmt, *args, tag=None):
        if self.log_level < 0: # silent
            return

        if len(args) > 0:
            fmt = fmt.format(*args)
        if tag is not None:
            fmt = '=={}==\t{}'.format(tag, fmt)

        # TODO: logging to file
        print(fmt)

    def debug(self, *args):
        if self.log_level >= DEBUG:
            self.log(*args, tag=DEBUG_TAG)
    
    def info(self, *args):
        if self.log_level >= INFO:
            self.log(*args, tag=INFO_TAG)

    def warn(self, *args):
        if self.log_level >= WARN:
            self.log(*args, tag=WARN_TAG)

    def error(self, *args):
        if self.log_level >= ERROR:
            self.log(*args, tag=ERROR_TAG)

    def promptYes(self, prompt, default):
        if default:
            d, a = 'y', 'n'
        else:
            a, d = 'y', 'n'
        if self.yes:
            self.warn('{} {} (--yes specified)', prompt, d.upper())
            return default
        else:
            r = itv.promptSelect(prompt, [a], default=d)
            return r.lower() == 'y'.lower()



'''
Represents options passed to Boatswain, merged with configurations read from
configuration file. They are readily accessible as attributes.

The only exception are the canvas and github tokens. Those may not be needed,
in which case they can be lazily accessed through the BoatswainConfig. They
should be accessed with the .githubToken() and .canvasToken() methods below.

This object also doubles as argument parser to read in those arguments, to
populate those option attributes. This all takes place during initialization.
'''

def ParseOption(
        argv,               # arguments to be parsed
        section=None,       # config section to grab defaults from
        config_path=None,   # override default config path
        desc=None,          # description for argument parser
        parse_deco=None,    # arg parser decorator to add addition args
        req_canvas=False,   # require canvas token
        req_github=False,   # require github token
        *args, **kwargs):   # other options passed to argparser

    if desc is None:
        desc = '[[ Base Boatswain argument parser ]]'

    if config_path is None:
        config_path = DEFAULT_INI_PATH

    parser = argparse.ArgumentParser(description=desc, *args, **kwargs)

    parser.add_argument('-n', '--noop',
                        default=False,
                        action='store_true',
                        help='do not perform action; for testing',
    )

    parser.add_argument('-y', '--yes',
                        default=False,
                        action='store_true',
                        help='automatic yes to prompts, non-interactive',
    )

    lvl_parser = parser.add_mutually_exclusive_group()
    lvl_parser.add_argument('--silent',
                        default=False,
                        action='store_true',
                        help='supress all output',
    )
    lvl_parser.add_argument('-q', '--quiet',
                        default=False,
                        action='store_true',
                        help='supress warnings',
    )
    lvl_parser.add_argument('-v', '--verbose',
                        default=False,
                        action='store_true',
                        help='verbose output',
    )
    lvl_parser.add_argument('--debug',
                        default=False,
                        action='store_true',
                        help='debug mode; enable all output',
    )

    


    config = BoatswainConfig(config_path)

    if req_canvas:
        try:
            canvasToken = config.canvasToken()
            parser.add_argument('--canvas-token',
                                default=canvasToken,
                                type=str,
                                help='override Boatswain Canvas token',
                                metavar='<canvas-token>',
            )
        # handle incomplete config; don't handle NoSectionError because we
        # assume that the canvas and github sections at least exist
        except configparser.NoOptionError:
            parser.add_argument('canvas_token',
                                type=str,
                                help='Canvas LMS auth token',
                                metavar='<canvas-token>',
            )

    if req_github:
        try:
            githubToken = config.githubToken()
            parser.add_argument('--github-token',
                                default=githubToken,
                                type=str,
                                help='override Boatswain GitHub token',
                                metavar='<github-token>',
            )
        # handle incomplete config; don't handle NoSectionError because we
        # assume that the canvas and github sections at least exist
        except configparser.NoOptionError:
            parser.add_argument('github_token',
                                type=str,
                                help='GitHub auth token',
                                metavar='<github-token>',
            )
    else:
        parser.github_token = None


    if parse_deco is not None:
        parse_deco(parser)

    '''
    Set the defaults to anything specified in that section of the config.
    Useful for saving defaults in a local config.
    '''
    if section is not None and section in config.sections():
        parser.set_defaults(**dict(config.items(section)))

    opt = parser.parse_args(argv)

    opt.__class__ = BoatswainOption
    opt.config = config

    if opt.debug:
        opt.log_level = DEBUG
    elif opt.verbose:
        opt.log_level = INFO
    elif opt.quiet:
        opt.log_level = ERROR
    elif opt.silent:
        opt.log_level = SILENT
    else:
        opt.log_level = WARN

    return opt


######## Interactive Boatswain Config Bootstrapper ########

def newPopulatedConfigInteractive():
    config = configparser.ConfigParser()
    config.add_section(CANVAS_SECTION)
    config.add_section(GITHUB_SECTION)

    i = itv.promptSelect('Configure Canvas token?', ['n'], default='y')
    if i == 'y':
        itv.output('You can generate a new Canvas token by going to your '
                'Canvas Profile -> Settings -> Approved Integrations '
                'and clicking on "+New Access Token"')
        canvasToken = itv.promptInput('Enter Canvas auth token')
        config.set(CANVAS_SECTION, CANVAS_TOKEN, canvasToken)

    i = itv.promptSelect('Configure GitHub token?', ['n'], default='y')
    if i == 'y':
        githubToken = itv.promptInput('Enter GitHub auth token')
        config.set(GITHUB_SECTION, GITHUB_TOKEN, githubToken)

    return config


def createConfigInteractive():
    try:
        itv.output('This script will help you create your Boatswain config.')
        path = itv.promptValidate('Enter Boatswain config file location', 
                itv.newFileValidator(), default=DEFAULT_INI_PATH)
        
        config = newPopulatedConfigInteractive()
        config.write(open(path, 'w+'))

        itv.output('Boatswain config file created at {}'.format(path))

    except EOFError:
        itv.output()
        itv.output('Quitting intercative Boatswaing config creator...')
        return


def main():
    itv.output('Welcome to Boatswain.')
    createConfigInteractive()


if __name__ == '__main__':
    main()
