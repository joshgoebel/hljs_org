import os
import traceback
import subprocess
import re
import logging
import shutil
import json
import importlib

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from django.conf import settings

from hljs_org import lib, models


log = logging.getLogger('hljs_org.updatehljs')


def import_file(filename):
    name, _ = os.path.splitext(os.path.basename(filename))
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run(args):
    output = subprocess.check_output(args, stderr=subprocess.STDOUT)
    return output.decode().splitlines()


def npm_publish(path):
    log.info('Looking to publishing %s to npm...' % path)
    package = json.load(open(os.path.join(path, 'package.json')))
    lines = run(['npm', 'view', package['name'], 'version'])
    lines = [l for l in lines if l and not l.startswith('npm')]
    published_version = lines[0]
    log.info('Found published %s=%s' % (package['name'], published_version))
    if published_version != package['version']:
        log.info('Publishing version %s to npm...' % package['version'])
        run(['npm', 'publish', path])
    else:
        log.info('Not publishing version %s over the same' % package['version'])


class Command(BaseCommand):
    help = 'Updates the site for a new version of highlight.js library'
    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('version', type=str)

    def _handle(self, version):
        '''
        The actual command handling extracted into a separate method to avoid
        an extra level of indentation inside the try..except in self.handle().
        '''
        os.chdir(settings.HLJS_SOURCE)
        log.info('Checking out version %s...' % version)
        run(['git', 'checkout', 'master'])
        run(['git', 'pull', '-f'])
        run(['git', 'pull', '-f', '--tags'])
        run(['git', 'checkout', version])

        log.info('Checking version consistency within the source...')
        version_numbers = version.split('.')
        node_version = version if len(version_numbers) >= 3 else '%s.0' % version
        short_version = version if len(version_numbers) <= 2 else '.'.join(version_numbers[:2])
        assert lib.version(settings.HLJS_SOURCE) == version
        assert re.search(r'"version"\s*:\s*"%s"' % node_version, open('package.json', encoding='utf-8').read()) is not None
        conf = import_file('docs/conf.py')
        assert conf.version == short_version
        assert conf.release == version

        log.info('Reinstalling node dependencies...')
        run(['rm', '-rf', 'node_modules'])
        run(['npm', 'install'])

        log.info('Building CDN build to populate cache...')
        run(['nodejs', 'tools/build.js', '--target', 'cdn'])
        log.info('Moving CDN build over to %s' % settings.HLJS_CACHE)
        if os.path.exists(settings.HLJS_CACHE):
            shutil.rmtree(settings.HLJS_CACHE)
        shutil.move('build', settings.HLJS_CACHE)

        # pretty sure we don't need, but can't hurt
        os.chdir(settings.HLJS_SOURCE)

        call_command('publishtest')
        call_command('collectstatic', interactive=False)

        log.info('Updating news entry...')
        models.News.objects.update_or_create(
            defaults={
                'text': lib.news(settings.HLJS_SOURCE, version),
            },
            for_version=version,
        )

        log.info('Update to version %s completed.' % version)

    def handle(self, version, **options):
        update = models.Update.objects.create(version=version)
        try:
            self._handle(version)
        except Exception as e:
            log.error(str(e))
            update.error = traceback.format_exc()
            if isinstance(e, subprocess.CalledProcessError):
                update.error += '\n\n' + e.output.decode()
            raise
        finally:
            update.finished = timezone.now()
            update.save()
