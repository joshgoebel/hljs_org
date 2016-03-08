# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hljs_org', '0002_news_for_version'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Snippet',
        ),
    ]
