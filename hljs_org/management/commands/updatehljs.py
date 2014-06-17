import os
import subprocess
import re
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings

from hljs_org import lib


log = logging.getLogger('hljs_org.updatehljs')

class Command(BaseCommand):
    help = 'Updates the site for a new version of highlight.js library'

    requires_model_validation = False

    # def add_arguments(self, parser):
    #     parser.add_argument('version', type=str)

    def handle(self, version, **base_options):
        os.chdir(settings.HLJS_SOURCE)
        log.info('Checking out version %s...' % version)
        subprocess.check_call(['git', 'checkout', 'master'])
        subprocess.check_call(['git', 'pull'])
        subprocess.check_call(['git', 'checkout', version])

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

        log.info('Publishing to node.js...')
        subprocess.check_call(['python3', 'tools/build.py', '--target', 'node'])
        subprocess.check_call(['npm', 'publish', 'build'])

        if os.path.isfile(settings.HLJS_TOUCHFILE):
            log.info('Signaling site restart...')
            os.utime(settings.HLJS_TOUCHFILE)

        log.info('Update to version %s completed.' % version)
