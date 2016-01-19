# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('greetings', '0002_auto_20160115_1824'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='data',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
