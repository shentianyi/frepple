# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-22 18:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('execute', '0004_auto_20181008_1913'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataStagingLog',
            fields=[
                ('source', models.CharField(blank=True, db_index=True, max_length=300, null=True, verbose_name='source')),
                ('lastmodified', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='last modified')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='updated_at')),
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, verbose_name='identifier')),
                ('nr', models.CharField(db_index=True, editable=False, max_length=300, verbose_name='nr')),
                ('create_user_nr', models.CharField(blank=True, db_index=True, editable=False, max_length=100, null=True, verbose_name='create_user_nr')),
                ('input_data', models.TextField(blank=True, null=True, verbose_name='input_data')),
                ('output_data', models.TextField(blank=True, null=True, verbose_name='output_data')),
                ('result', models.BooleanField(default=False, verbose_name='result')),
                ('message', models.TextField(blank=True, null=True, verbose_name='message')),
                ('start_at', models.DateTimeField(blank=True, null=True, verbose_name='start_at')),
                ('end_at', models.DateTimeField(blank=True, null=True, verbose_name='end_at')),
            ],
            options={
                'verbose_name': 'data_staging_log',
                'verbose_name_plural': 'data_staging_logs',
                'db_table': 'data_staging_log',
                'abstract': False,
            },
        ),
    ]