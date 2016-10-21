import os
import traceback
import subprocess
import re
import logging
import shutil

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from django.conf import settings

from hljs_org import lib, models


log = logging.getLogger('hljs_org.updatehljs')

def run(args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT)

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
        run(['git', 'checkout', version])

        log.info('Checking version consistency within the source...')
        version_numbers = version.split('.')
        node_version = version if len(version_numbers) >= 3 else '%s.0' % version
        short_version = version if len(version_numbers) <= 2 else '.'.join(version_numbers[:2])
        assert lib.version(settings.HLJS_SOURCE) == version
        assert re.search(r'"version"\s*:\s*"%s"' % node_version, open('package.json', encoding='utf-8').read()) is not None
        conf = open('docs/conf.py', encoding='utf-8').read()
        assert re.search('version = \'%s\'' % short_version, conf) is not None
        assert re.search('release = \'%s\'' % version, conf) is not None

        log.info('Updating node dependencies...')
        run(['npm', 'update'])

        log.info('Building CDN build to populate cache...')
        run(['nodejs', 'tools/build.js', '--target', 'cdn', 'none'])
        log.info('Moving CDN build over to %s' % settings.HLJS_CACHE)
        if os.path.exists(settings.HLJS_CACHE):
            shutil.rmtree(settings.HLJS_CACHE)
        shutil.move('build', settings.HLJS_CACHE)

        log.info('Updating CDN repo at %s' % settings.HLJS_CDN_SOURCE)
        run(['nodejs', 'tools/build.js', '--target', 'cdn', ':common'])
        os.chdir(settings.HLJS_CDN_SOURCE)
        run(['git', 'pull', '-f'])
        lines = run(['git', '--git-dir', os.path.join(settings.HLJS_CDN_SOURCE, '.git'), 'tag']).decode('utf-8').splitlines()
        if version in lines:
            log.info('Tag %s already exists in the local CDN repo' % version)
        else:
            build_dir = os.path.join(settings.HLJS_CDN_SOURCE, 'build')
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
            shutil.move(os.path.join(settings.HLJS_SOURCE, 'build'), build_dir)
            run(['git', 'add', '.'])
            run(['git', 'commit', '-m', 'Update to version %s' % version])
            run(['git', 'tag', version])
        run(['git', 'push'])
        run(['git', 'push', '--tags'])
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

        lines = run(['npm', 'view', 'highlight.js', 'version']).decode('utf-8').splitlines()
        lines = [l for l in lines if l and not l.startswith('npm')]
        published_version = lines[0]
        log.info('Published npm version is %s' % published_version)
        if published_version != node_version:
            log.info('Publishing version %s to npm...' % node_version)
            run(['nodejs', 'tools/build.js', '--target', 'node'])
            run(['npm', 'publish', 'build'])

        log.info('Update to version %s completed.' % version)

    def handle(self, version, **options):
        update = models.Update.objects.create(version=version)
        try:
            self._handle(version)
        except Exception as e:
            log.error(str(e))
            update.error = traceback.format_exc()
            if isinstance(e, subprocess.CalledProcessError):
                update.error += '\n\n' + e.output.decode('utf-8')
            raise
        finally:
            update.finished = timezone.now()
            update.save()
