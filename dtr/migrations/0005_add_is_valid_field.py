# Generated migration for adding is_valid field to DTRLog

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtr', '0004_add_dtr_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='dtrlog',
            name='is_valid',
            field=models.BooleanField(
                default=True,
                help_text="Whether this time-in is valid. Set to False when DTR is rejected."
            ),
        ),
    ]
