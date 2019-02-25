# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import logging

from django.core.management.base import BaseCommand
from django.conf import settings


log = logging.getLogger('hljs_org.publishtest')


def run(args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT)


def build_highlightjs(languages=[]):
    run(['nodejs', os.path.join('tools', 'build.js'),
        '--target', 'browser', '--docs',
    ] + languages)


class Command(BaseCommand):
    help = 'Publishes the demo on the Web. This requires up to date cache for building highlight.pack.js'
    requires_system_check = False

    def handle(self, *args, **options):
        # ensure we're working with the absolute static_root as we'll have to
        # chdir into highlight.js source because of how its build tool works
        static_root = os.path.abspath(settings.STATIC_ROOT)
        os.chdir(settings.HLJS_SOURCE)
        log.info('Publishing test page to %s' % static_root)
        build_path = os.path.join(settings.HLJS_SOURCE, 'build')

        log.info('Building full browser build...')
        build_highlightjs()

        log.info('Copying highlight.pack.js...')
        shutil.copy(os.path.join(build_path, 'highlight.pack.js'), static_root)

        log.info('Copying demo...')
        demo_dst = os.path.join(static_root, 'demo')
        if os.path.exists(demo_dst):
            shutil.rmtree(demo_dst)
        shutil.copytree(os.path.join(build_path, 'demo'), demo_dst)

        log.info('Building browser build for [%s]...' % ' '.join(settings.HLJS_SNIPPETS))
        build_highlightjs(settings.HLJS_SNIPPETS)

        log.info('Copying highlight.site.pack.js...')
        shutil.copy(
            os.path.join(build_path, 'highlight.pack.js'),
            os.path.join(static_root, 'highlight.site.pack.js')
        )
