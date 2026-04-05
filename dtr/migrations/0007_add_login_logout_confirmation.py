# Generated migration for adding login/logout confirmation fields to DTRLog

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dtr', '0006_add_is_resubmission_field'),
    ]

    operations = [
        # Login confirmation fields
        migrations.AddField(
            model_name='dtrlog',
            name='login_confirmation_status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected')],
                default='pending',
                help_text='Supervisor confirmation status for login (time_in)',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='dtrlog',
            name='login_confirmed_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Supervisor who confirmed/rejected the login',
                limit_choices_to={'role': 'supervisor'},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='login_confirmed_dtr_logs',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='dtrlog',
            name='login_confirmed_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the login was confirmed/rejected',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='dtrlog',
            name='login_remarks',
            field=models.TextField(
                blank=True,
                help_text="Supervisor's remarks for login confirmation/rejection",
            ),
        ),
        # Logout confirmation fields
        migrations.AddField(
            model_name='dtrlog',
            name='logout_confirmation_status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected')],
                default='pending',
                help_text='Supervisor confirmation status for logout (time_out)',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='dtrlog',
            name='logout_confirmed_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Supervisor who confirmed/rejected the logout',
                limit_choices_to={'role': 'supervisor'},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='logout_confirmed_dtr_logs',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='dtrlog',
            name='logout_confirmed_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the logout was confirmed/rejected',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='dtrlog',
            name='logout_remarks',
            field=models.TextField(
                blank=True,
                help_text="Supervisor's remarks for logout confirmation/rejection",
            ),
        ),
    ]
