# Generated manually for supervisor confirmation feature

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dtr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dtrlog',
            name='confirmation_status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected')],
                default='pending',
                help_text='Supervisor confirmation status for this DTR log',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='dtrlog',
            name='confirmed_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the log was confirmed/rejected',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='dtrlog',
            name='confirmed_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Supervisor who confirmed/rejected this log',
                limit_choices_to={'role': 'supervisor'},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='confirmed_dtr_logs',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='dtrlog',
            name='confirmation_remarks',
            field=models.TextField(
                blank=True,
                help_text="Supervisor's remarks for confirmation/rejection"
            ),
        ),
    ]
