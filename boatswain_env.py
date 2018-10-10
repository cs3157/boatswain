
import configparser
import os

import interactive as itv

DEFAULT_INI_PATH = os.path.expanduser('~/.boatswain.ini')

CANVAS_SECTION = 'canvas'
CANVAS_TOKEN = 'token'

GITHUB_SECTION = 'github'
GITHUB_TOKEN = 'token'

class BoatswainConfig(configparser.ConfigParser):
    def __init__(self, path=DEFAULT_INI_PATH):
        super().__init__()
        self.path = path
        self.read(path)

    def canvasToken(self):
        return self[CANVAS_SECTION][CANVAS_TOKEN]

    def githubToken(self):
        return self[GITHUB_SECTION][GITHUB_TOKEN]


"""
Takes a parser and sets the defaults to anything specified in that section
of the local boatswain config file
"""
def populateDefaults(config, parser, section):
    if section in config.sections():
        parser.set_defaults(**dict(config.items(section)))


"""
Takes a parser and some arguments, and overrides some of the 

Returns a tuple of the parsed 
"""
def envParse(section, parser, args, config_path=None):
    if config_path is None:
        config_path = DEFAULT_INI_PATH

    config = BoatswainConfig(config_path)
    populateDefaults(config, parser, section)
    return parser.parse_args(args), config


def newPopulatedConfigInteractive():
    config = configparser.ConfigParser()
    config.add_section(CANVAS_SECTION)
    config.add_section(GITHUB_SECTION)

    i = itv.promptSelect('Do you have a Canvas token?', ['n'], default='y')
    if i == 'y':
        canvasToken = itv.promptInput('Enter Canvas auth token')
        config.set(CANVAS_SECTION, CANVAS_TOKEN, canvasToken)

    i = itv.promptSelect('Do you have a GitHub token?', ['n'], default='y')
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

    except EOFError:
        itv.output()
        itv.output('Quitting intercative Boatswaing config creator...')
        return


def main():
    itv.output('Welcome to Boatswain.')
    createConfigInteractive()


if __name__ == '__main__':
    main()
