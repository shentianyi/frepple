from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0037_auto_20190124_1820'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Demand',

        ),
    ]
