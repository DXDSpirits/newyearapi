# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Greeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner_id', models.IntegerField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('title', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('key', models.CharField(db_index=True, max_length=200, null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('data', jsonfield.fields.JSONField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.SlugField(blank=True, null=True, choices=[(b'province', b'Province'), (b'city', b'City'), (b'district', b'District')])),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('parent', models.ForeignKey(blank=True, to='greetings.Place', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='greeting',
            name='places',
            field=models.ManyToManyField(related_name='greetings', to='greetings.Place', blank=True),
        ),
    ]
