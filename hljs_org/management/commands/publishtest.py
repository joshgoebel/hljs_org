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
        log.info('Publishing test page to %s' % settings.STATIC_ROOT)
        src_path = os.path.join(settings.HLJS_SOURCE, 'src')
        build_path = os.path.join(settings.HLJS_SOURCE, 'build')
        tools_path = os.path.join(settings.HLJS_SOURCE, 'tools')

        log.info('Building full browser build...')
        run(['python3', os.path.join(tools_path, 'build.py'), '--target', 'browser'])

        log.info('Copying highlight.pack.js...')
        shutil.copy(os.path.join(build_path, 'highlight.pack.js'), settings.STATIC_ROOT)

        log.info('Copying test.html...')
        test = open(os.path.join(src_path, 'test.html'), encoding='utf-8').read()
        test = test.replace('../build/highlight.pack.js', 'highlight.pack.js')
        open(os.path.join(settings.STATIC_ROOT, 'test.html'), 'w', encoding='utf-8').write(test)

        log.info('Copying styles...')
        styles_dst = os.path.join(settings.STATIC_ROOT, 'styles')
        if os.path.exists(styles_dst):
            shutil.rmtree(styles_dst)
        shutil.copytree(os.path.join(src_path, 'styles'), styles_dst)
