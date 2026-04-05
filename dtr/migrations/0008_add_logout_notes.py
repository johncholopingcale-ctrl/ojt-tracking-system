# Generated migration for adding logout_notes field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtr', '0007_add_login_logout_confirmation'),
    ]

    operations = [
        migrations.AddField(
            model_name='dtrlog',
            name='logout_notes',
            field=models.TextField(blank=True, help_text="Notes about the day's activities added during logout"),
        ),
    ]
