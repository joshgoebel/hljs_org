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

class Command(BaseCommand):
    help = 'Publishes test.html on the Web. This requires up to date cache for building highlight.pack.js'
    requires_system_check = False

    def handle(self, *args, **options):
        os.chdir(settings.HLJS_SOURCE)
        log.info('Publishing test page to %s' % settings.STATIC_ROOT)
        build_path = os.path.join(settings.HLJS_SOURCE, 'build')
        tools_path = os.path.join(settings.HLJS_SOURCE, 'tools')

        log.info('Building full browser build...')
        run(['nodejs', os.path.join(tools_path, 'build.js'), '--target', 'browser'])

        log.info('Copying highlight.pack.js...')
        shutil.copy(os.path.join(build_path, 'highlight.pack.js'), settings.STATIC_ROOT)

        log.info('Copying demo...')
        demo_dst = os.path.join(settings.STATIC_ROOT, 'demo')
        if os.path.exists(demo_dst):
            shutil.rmtree(demo_dst)
        shutil.copytree(os.path.join(build_path, 'demo'), demo_dst)
