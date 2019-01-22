# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-22 17:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0018_create_intentorypara'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesOrder',
            fields=[
                ('source', models.CharField(blank=True, db_index=True, max_length=300, null=True, verbose_name='source')),
                ('lastmodified', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='last modified')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='updated_at')),
                ('id', models.AutoField(help_text='Unique identifier', primary_key=True, serialize=False, verbose_name='id')),
                ('nr', models.CharField(blank=True, db_index=True, max_length=300, null=True, unique=True, verbose_name='nr')),
                ('status', models.CharField(blank=True, choices=[('open', 'open'), ('close', 'close'), ('canceled', 'canceled'), ('invoiced', 'invoiced')], max_length=20, null=True, verbose_name='status')),
                ('max_lateness', models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True, verbose_name='max lateness')),
                ('min_shipment', models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True, verbose_name='min shipment')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='salesorder_customer', to='input.Customer', verbose_name='customer')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salesorder_location', to='input.Location', verbose_name='location')),
            ],
            options={
                'verbose_name': 'sales order',
                'verbose_name_plural': 'sales orders',
                'db_table': 'salesorder',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
