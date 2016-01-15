# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('greetings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='greeting',
            name='status',
            field=models.SlugField(default=b'raw', choices=[(b'raw', b'Raw'), (b'online', b'Online'), (b'archived', b'Archived')]),
        ),
        migrations.AlterField(
            model_name='greeting',
            name='owner_id',
            field=models.IntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='category',
            field=models.SlugField(default=b'city', choices=[(b'province', b'Province'), (b'city', b'City'), (b'district', b'District')]),
        ),
    ]
