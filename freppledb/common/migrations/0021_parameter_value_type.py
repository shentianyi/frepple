# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-23 17:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0020_auto_20181109_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameter',
            name='value_type',
            field=models.CharField(choices=[('string', 'string'), ('int', 'int'), ('number', 'number'), ('datetime', 'datetime')], default='string', max_length=100, verbose_name='value_type'),
        ),
    ]
