# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('greetings', '0003_place_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inspiration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('places', models.ManyToManyField(related_name='inspirations', to='greetings.Place', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('greeting', models.ForeignKey(blank=True, to='greetings.Greeting', null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=set([('greeting', 'user_id')]),
        ),
    ]
