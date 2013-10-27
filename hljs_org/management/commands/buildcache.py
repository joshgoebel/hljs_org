# -*- coding: utf-8 -*-
import sys
import os
import logging

from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings

import build

log = logging.getLogger('hljs_org.buildcache')

class Command(NoArgsCommand):
    help = 'Rebuilds compressed files cache'

    requires_model_validation = False

    def handle(self, **base_options):
        tools_path = os.path.join(settings.HLJS_SOURCE, 'tools')
        src_path = os.path.join(settings.HLJS_SOURCE, 'src')
        filenames = build.language_filenames(src_path, [])
        filenames.append(os.path.join(src_path, 'highlight.js'))
        for filename in filenames:
            outputname = os.path.join(settings.HLJS_CACHE, os.path.basename(filename))
            log.info('Writing %s' % outputname)
            open(outputname, 'w').write(build.compress_content(tools_path, build.strip_read(filename)))
