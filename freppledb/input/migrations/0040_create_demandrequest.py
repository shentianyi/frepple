# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-24 18:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('input', '0039_demand'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemandRequest',
            fields=[
                ('source', models.CharField(blank=True, db_index=True, max_length=300, null=True, verbose_name='source')),
                ('lastmodified', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='last modified')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='updated_at')),
                ('id', models.AutoField(help_text='Unique identifier', primary_key=True, serialize=False, verbose_name='id')),
                ('type', models.CharField(choices=[('manufacture', 'manufacture'), ('purchase', 'purchase')], max_length=20, verbose_name='type')),
                ('qty', models.DecimalField(blank=True, db_index=True, decimal_places=8, max_digits=20, null=True, verbose_name='qty')),
                ('due', models.DateTimeField(blank=True, null=True, verbose_name='due')),
                ('status', models.CharField(blank=True, choices=[('init', 'init'), ('open', 'open'), ('release', 'release'), ('closed', 'closed'), ('canceled', 'canceled')], max_length=20, null=True, verbose_name='status')),
                ('priority', models.IntegerField(blank=True, default=0, null=True, verbose_name='priority')),
                ('max_lateness', models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True, verbose_name='max lateness')),
                ('min_shipment', models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True, verbose_name='min shipment')),
                ('closed_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='closed at')),
                ('demand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandrequest_demand', to='input.Demand', verbose_name='demand')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandrequest_item', to='input.Forecast', verbose_name='item')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandrequest_location', to='input.Location', verbose_name='location')),
            ],
            options={
                'verbose_name': 'demand request',
                'verbose_name_plural': 'demand requests',
                'db_table': 'demand_request',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DemandRequestVersion',
            fields=[
                ('source', models.CharField(blank=True, db_index=True, max_length=300, null=True, verbose_name='source')),
                ('lastmodified', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='last modified')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='updated_at')),
                ('id', models.AutoField(help_text='Unique identifier', primary_key=True, serialize=False, verbose_name='id')),
                ('nr', models.CharField(db_index=True, editable=False, max_length=300, verbose_name='nr')),
                ('status', models.CharField(choices=[('init', 'init'), ('canceled', 'canceled'), ('release', 'release'), ('closed', 'closed')], max_length=20, verbose_name='status')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandrequest_create_user', to=settings.AUTH_USER_MODEL, verbose_name='create_user')),
            ],
            options={
                'verbose_name': 'demand request version',
                'verbose_name_plural': 'demand request versions',
                'db_table': 'demand_request_version',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='demandrequest',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandrequest_demandversion', to='input.DemandRequestVersion', verbose_name='demand request version'),
        ),
    ]
