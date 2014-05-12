# coding: utf-8
from fabric.api import env, cd, run, local, get


env['hosts'] = ['highlightjs.org']
SRC = '/home/maniac/code/highlight'
CACHE = '/home/maniac/app-data/hljs_cache'
MANAGE = '/home/maniac/hljs_org/manage.py'


def checkout(version):
    with cd(SRC):
        run('git checkout master')
        run('git pull')
        run('git checkout %s' % version)

def check_version(version):
    node_version = version if len(version.split('.')) >= 3 else '%s.0' % version
    with cd(SRC):
        run('grep \'Version %s\' CHANGES.md' % version)
        run('grep \'"version" : "%s"\' src/package.json' % node_version)
        run('grep "version = \'%s\'" docs/conf.py' % version)
        run('grep "release = \'%s\'" docs/conf.py' % version)

def publish_site():
    run('%s buildcache' % MANAGE)
    run('%s publishtest' % MANAGE)
    run('%s collectstatic --noinput' % MANAGE)
    run('touch /etc/uwsgi/apps-available/hljs_org.ini')

def publish_node():
    with cd(SRC):
        run('python3 tools/build.py --target node')
        run('npm publish build')

def publish_cdn(version):
    with cd(SRC):
        run('python3 tools/build.py --target cdn :common')
        with cd('build'):
            zipname = 'highlight.js-%s.zip' % version
            run('zip -r %s *' % zipname)
            path = get(zipname, '')[0]
            local('mv %s .' % path)
            local('rmdir %s' % env['hosts'][0])
    return zipname

def print_memo(zipname):
    print 'TODO:'
    if zipname:
        print '- send %s to Yandex' % zipname
    print '- write news'

def publish(version):
    checkout(version)
    check_version(version)
    publish_site()
    zipname = publish_cdn(version)
    publish_node()
    print_memo(zipname)

def update_smorg():
    with cd('/var/www/media/js/highlight'):
        run('./update.sh')
