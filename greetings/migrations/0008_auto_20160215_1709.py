# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('greetings', '0007_relay'),
    ]

    operations = [
        migrations.AlterField(
            model_name='greeting',
            name='status',
            field=models.SlugField(default='raw', choices=[('raw', 'Raw'), ('online', 'Online'), ('archived', 'Archived')]),
        ),
        migrations.AlterField(
            model_name='place',
            name='category',
            field=models.SlugField(default='city', choices=[('province', 'Province'), ('city', 'City'), ('district', 'District')]),
        ),
    ]
