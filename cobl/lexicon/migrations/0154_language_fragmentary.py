# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-08 18:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lexicon', '0153_nexusexport__exporttabledata'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='fragmentary',
            field=models.BooleanField(default=0),
        ),
    ]