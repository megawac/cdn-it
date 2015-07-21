#!/usr/bin/python

import github3, inquirer, requests

import fileinput, sys, json
from optparse import OptionParser

def is_url(url):
    return '://' in url

parser = OptionParser()
parser.add_option('-f', '--file', dest='filename',
                  help='Input package.json,component.json or bower.json', metavar='FILE')
parser.add_option('-t', '--token', dest='token',
                  help='Github API token', metavar='TOKEN')

(options, args) = parser.parse_args()

# if options.token is None:
#     raise Exception('Github API token required')
# elif len(args) < 1:
#     raise Exception('Must provide a file (cdn-it package.json)')

if not is_url(args[0]):
    with open(args[0], 'r') as f:
        config = json.loads(f.read())
else:
    config = requests.get(args[0]).json()

# Best effort - attempt to determine the fields for info.ini and update.json

answers = inquirer.prompt([
    inquirer.Text('name', message="Project name",
        default=next(v for k,v in config.iteritems() if 'name' in k)
    ),
    inquirer.Text('desc', message="Description",
        default=next(v for k,v in config.iteritems() if 'desc' in k)
    )
])
name = answers['name']
desc = answers['desc']

author = next((v for k,v in config.iteritems() if 'author' in k), name)

# Some people like making this a list or dictionary or list of dicts...
if type(author) == list:
    author = author[0]
if type(author) == dict:
    author = author['name'] or name

if 'repository' in config:
    repo = config['repository']
    if type(repo) == dict:
        repo = repo['url']

answers = inquirer.prompt([
    inquirer.Text('author', message="Author", default=author),
    inquirer.Text('repo', message="Repository", default=repo)
])
author = answers['author']
repo = answers['repo']

def format_clude(clude):
    return [x.strip() for x in clude.split(',')]

answers = inquirer.prompt([
    inquirer.Text('homepage', message="homepage",
        default=next((v for v in config.itervalues() if is_url(v) and repo not in v), repo)
    ),
    inquirer.Text('mainfile', message="mainfile"),
    inquirer.List('pkg',
        message="Update package manager",
        choices=['github', 'npm', 'bower'],
    ),
    inquirer.Text('basePath', message="basePath", default='/'),
    inquirer.Text('include', message="include", default='**/*'),
    inquirer.Text('exclude', message="exclude")
])
homepage = answers['homepage']
mainfile = answers['mainfile']
pkg = answers['pkg']
basePath = answers['basePath']
include = format_clude(answers['include'])
exclude = format_clude(answers['exclude'])

# TODO push to github