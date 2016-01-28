# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('greetings', '0004_auto_20160128_2038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='like',
            old_name='user_id',
            new_name='owner_id',
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=set([('greeting', 'owner_id')]),
        ),
    ]
