# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-23 19:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0029_rename_filed_of_inventorypara'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='purchase_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='purchaseorderitem_purchase_order', to='input.PurchaseOrder', verbose_name='purchase order'),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='status',
            field=models.CharField(blank=True, choices=[('open', 'open'), ('closed', 'closed'), ('canceled', 'canceled'), ('invoiced', 'invoiced')], max_length=20, null=True, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='salesorderitem',
            name='status',
            field=models.CharField(blank=True, choices=[('open', 'open'), ('closed', 'closed'), ('canceled', 'canceled'), ('invoiced', 'invoiced')], max_length=20, null=True, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='nr',
            field=models.CharField(max_length=300, verbose_name='nr'),
        ),
    ]
