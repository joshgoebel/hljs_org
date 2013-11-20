# -*- coding: utf-8 -*-
import os
import shutil
import logging

from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings

import build

log = logging.getLogger('hljs_org.publishtest')


class Command(NoArgsCommand):
    help = 'Publishes test.html on the Web. This requires up to date cache for building highlight.pack.js'

    requires_model_validation = False

    def handle(self, **base_options):
        src_path = os.path.join(settings.HLJS_SOURCE, 'src')
        log.info('Source path: %s' % src_path)
        log.info('Destination path: %s' % settings.STATIC_ROOT)

        filenames = build.language_filenames(src_path, [])
        filenames = [os.path.join(settings.HLJS_CACHE, os.path.basename(f)) for f in filenames]
        log.info('Building highlight.pack.js with %s languages' % len(filenames))
        hljs = build.glue_files(os.path.join(settings.HLJS_CACHE, 'highlight.js'), filenames, True)
        open(os.path.join(settings.STATIC_ROOT, 'highlight.pack.js'), 'w', encoding='utf-8').write(hljs)

        log.info('Copying test.html')
        test = open(os.path.join(src_path, 'test.html'), encoding='utf-8').read()
        test = test.replace('../build/highlight.pack.js', 'highlight.pack.js')
        open(os.path.join(settings.STATIC_ROOT, 'test.html'), 'w', encoding='utf-8').write(test)

        log.info('Copying styles')
        styles_dst = os.path.join(settings.STATIC_ROOT, 'styles')
        if os.path.exists(styles_dst):
            shutil.rmtree(styles_dst)
        shutil.copytree(os.path.join(src_path, 'styles'), styles_dst)
