#!/usr/bin/python

import github3, inquirer, requests

import fileinput, sys, json
from optparse import OptionParser
from urlparse import urlparse
from time import sleep

def is_url(url):
    return '://' in url

def main():
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='filename',
                      help='Input package.json,component.json or bower.json', metavar='FILE')
    parser.add_option('-t', '--token', dest='token',
                      help='Github API token', metavar='TOKEN')

    (options, args) = parser.parse_args()

    if options.token is None:
        raise Exception('Github API token required')
    elif len(args) < 1:
        raise Exception('Must provide a file (cdn-it package.json)')

    gh = github3.login(token=options.token)
    me = gh.me()

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
    author = answers['author'].strip()
    repo = answers['repo'].strip()

    def format_clude(clude):
        return filter(bool, [x.strip() for x in clude.split(',')])

    answers = inquirer.prompt([
        inquirer.Text('homepage', message="homepage",
            default=next((v for v in config.itervalues() if is_url(v) and repo not in v), repo)
        ),
        inquirer.Text('mainfile', message="mainfile"),
        inquirer.List('pkg',
            message="Package manager for updates",
            choices=['github', 'npm', 'bower'],
        ),
        inquirer.Text('basePath', message="basePath", default='/'),
        inquirer.Text('include', message="include", default='**/*'),
        inquirer.Text('exclude', message="exclude")
    ])
    homepage = answers['homepage'].strip()
    mainfile = answers['mainfile'].strip()
    pkg = answers['pkg'].strip()
    basePath = answers['basePath'].strip()
    include = format_clude(answers['include'])
    exclude = format_clude(answers['exclude'])

    update_repo = '/'.join(filter(bool, urlparse(repo).path.rstrip('.git').split('/')))

    # Push it all up to github
    upstream = gh.repository('jsdelivr', 'jsdelivr')
    origin = upstream.create_fork()

    commit = origin.commit('master')
    ref = origin.create_ref('refs/heads/%s' % name, commit.sha)

    files = {
        'info.ini': """author = "%s"
github = "%s"
homepage = "%s"
description = "%s"
mainfile = "%s"
""" % (author, repo, homepage, desc, mainfile),
    'update.json': """{
    "packageManager": %s,
    "name": %s,
    "repo": %s,
    "files": {
        "basePath": %s,
        "include": %s,
        "exclude": %s
    }
}""" % tuple(map(json.dumps, [pkg, name, update_repo, basePath, include, exclude]))
    }

    for fname,content in files.iteritems():
        origin.create_file('files/%s/%s' % (name, fname), 'Create %s for %s' % (fname, name), bytes(content), name)
        # Workaround github api glitch where we're too damn quick
        sleep(0.1)


    pr = upstream.create_pull('Create %s' % name,
        'master',
        '%s:%s' % (me.login, name),
        'Created via https://github.com/megawac/cdn-it'
    )

    print 'Created pull request %s' % pr.html_url

if __name__ == '__main__':  
    main()