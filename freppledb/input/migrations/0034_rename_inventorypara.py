from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0033_alter_purchaseorder_nr'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventoryparameter',
            old_name='safetysotck_min_qty',
            new_name='safetystock_min_qty',
        ),
        migrations.RenameField(
            model_name='inventoryparameter',
            old_name='safetysotck_max_qty',
            new_name='safetystock_max_qty',
        ),
    ]
