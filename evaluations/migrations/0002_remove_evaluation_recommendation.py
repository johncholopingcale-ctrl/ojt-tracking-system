# Generated migration to remove recommendation field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evaluation',
            name='recommendation',
        ),
    ]
