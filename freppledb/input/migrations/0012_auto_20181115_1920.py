# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-11-15 19:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0011_auto_20181115_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='lock_type',
            field=models.CharField(blank=True, choices=[('locked', 'locked'), ('unlocked', 'unlocked')], default='unlocked', max_length=20, null=True, verbose_name='lock type'),
        ),
    ]
