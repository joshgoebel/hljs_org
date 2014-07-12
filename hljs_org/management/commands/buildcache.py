# -*- coding: utf-8 -*-
import sys
import os
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

import build

log = logging.getLogger('hljs_org.buildcache')

class Command(BaseCommand):
    help = 'Rebuilds compressed files cache'
    requires_system_checks = False

    def handle(self, *args, **options):
        tools_path = os.path.join(settings.HLJS_SOURCE, 'tools')
        src_path = os.path.join(settings.HLJS_SOURCE, 'src')
        filenames = build.language_filenames(src_path, [])
        filenames.append(os.path.join(src_path, 'highlight.js'))
        for filename in filenames:
            outputname = os.path.join(settings.HLJS_CACHE, os.path.basename(filename))
            log.info('Writing %s' % outputname)
            open(outputname, 'w', encoding='utf-8').write(build.compress_content(tools_path, build.strip_read(filename)))
