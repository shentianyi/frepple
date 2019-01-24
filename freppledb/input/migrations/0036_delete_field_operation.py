from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('input', '0035_alter_fields_inventorypara'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='operationplan',
            name='demand',
        ),
    ]
