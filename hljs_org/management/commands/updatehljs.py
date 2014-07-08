import os
import traceback
import subprocess
import re
from datetime import datetime
import logging

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

from hljs_org import lib, models


log = logging.getLogger('hljs_org.updatehljs')

def run(args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT)

class Command(BaseCommand):
    help = 'Updates the site for a new version of highlight.js library'

    requires_model_validation = False

    # def add_arguments(self, parser):
    #     parser.add_argument('version', type=str)

    def do_handle(self, version):
        '''
        The actual command handling extracted into a separate method to avoid
        an extra level of indentation inside the try..except in self.handle().
        '''
        os.chdir(settings.HLJS_SOURCE)
        log.info('Checking out version %s...' % version)
        run(['git', 'checkout', 'master'])
        run(['git', 'pull'])
        run(['git', 'checkout', version])

        log.info('Checking version consistency within the source...')
        node_version = version if len(version.split('.')) >= 3 else '%s.0' % version
        assert lib.version(settings.HLJS_SOURCE) == version
        assert re.search('"version" : "%s"' % node_version, open('src/package.json').read()) is not None
        conf = open('docs/conf.py').read()
        assert re.search('version = \'%s\'' % version, conf) is not None
        assert re.search('release = \'%s\'' % version, conf) is not None

        call_command('buildcache')
        call_command('publishtest')
        call_command('collectstatic', interactive=False)
        call_command('updatecdns')

        log.info('Reading current published version on npm...')
        lines = run(['npm', 'view', 'highlight.js', 'version']).decode('utf-8').splitlines()
        lines = [l for l in lines if l and not l.startswith('npm')]
        published_version = lines[0]
        log.info('Published version is %s' % published_version)
        if published_version != node_version:
            log.info('Publishing version %s to npm...' % node_version)
            run(['python3', 'tools/build.py', '--target', 'node'])
            run(['npm', 'publish', 'build'])

        if os.path.isfile(settings.HLJS_TOUCHFILE):
            log.info('Signaling site restart...')
            os.utime(settings.HLJS_TOUCHFILE)

        log.info('Update to version %s completed.' % version)

    def handle(self, version, **base_options):
        update = models.Update.objects.create(version=version)
        try:
            self.do_handle(version)
        except Exception as e:
            log.error(str(e))
            update.error = traceback.format_exc()
            if isinstance(e, subprocess.CalledProcessError):
                update.error += '\n\n' + e.output.decode('utf-8')
            raise
        finally:
            update.finished = datetime.now()
            update.save()
