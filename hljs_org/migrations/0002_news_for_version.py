# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hljs_org', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='for_version',
            field=models.CharField(default='', blank=True, max_length=255),
            preserve_default=True,
        ),
    ]
