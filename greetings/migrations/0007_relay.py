# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('greetings', '0006_share'),
    ]

    operations = [
        migrations.CreateModel(
            name='Relay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner_id', models.IntegerField(unique=True, null=True, blank=True)),
                ('parent_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
