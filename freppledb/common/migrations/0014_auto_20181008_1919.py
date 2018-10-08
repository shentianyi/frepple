# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-10-08 19:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0013_currency_param'),
    ]

    operations = [
        migrations.AddField(
            model_name='bucket',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created at'),
        ),
        migrations.AddField(
            model_name='bucket',
            name='updated_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='updated at'),
        ),
        migrations.AddField(
            model_name='bucketdetail',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created at'),
        ),
        migrations.AddField(
            model_name='bucketdetail',
            name='updated_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='updated at'),
        ),
        migrations.AddField(
            model_name='comment',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created at'),
        ),
        migrations.AddField(
            model_name='comment',
            name='source',
            field=models.CharField(blank=True, db_index=True, max_length=300, null=True, verbose_name='source'),
        ),
        migrations.AddField(
            model_name='comment',
            name='updated_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='updated at'),
        ),
        migrations.AddField(
            model_name='parameter',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created at'),
        ),
        migrations.AddField(
            model_name='parameter',
            name='updated_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='updated at'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='lastmodified',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='last modified'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='object_pk',
            field=models.TextField(verbose_name='object id'),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='status',
            field=models.CharField(choices=[('free', 'free'), ('in use', 'in use'), ('busy', 'busy')], max_length=10, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='user',
            name='language',
            field=models.CharField(choices=[('auto', 'Detect automatically'), ('en', 'English'), ('fr', 'French'), ('de', 'German'), ('it', 'Italian'), ('ja', 'Japanese'), ('nl', 'Dutch'), ('pt', 'Portuguese'), ('pt-br', 'Brazilian Portuguese'), ('ru', 'Russian'), ('es', 'Spanish'), ('zh-cn', 'Simplified Chinese'), ('zh-tw', 'Traditional Chinese')], default='auto', max_length=10, verbose_name='language'),
        ),
        migrations.AlterField(
            model_name='user',
            name='theme',
            field=models.CharField(choices=[('earth', 'Earth'), ('grass', 'Grass'), ('lemon', 'Lemon'), ('odoo', 'Odoo'), ('openbravo', 'Openbravo'), ('orange', 'Orange'), ('snow', 'Snow'), ('strawberry', 'Strawberry'), ('water', 'Water')], default='earth', max_length=20, verbose_name='theme'),
        ),
    ]
