
import configparser
import os

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

