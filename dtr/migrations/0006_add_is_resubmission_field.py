# Generated migration for adding is_resubmission field to DTRLog

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtr', '0005_add_is_valid_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='dtrlog',
            name='is_resubmission',
            field=models.BooleanField(
                default=False,
                help_text="Whether this is a resubmitted DTR after rejection."
            ),
        ),
    ]
