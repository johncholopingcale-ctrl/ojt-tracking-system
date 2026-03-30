# Generated migration for DTR History model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dtr', '0003_dtrlog_logout_selfie'),
    ]

    operations = [
        migrations.CreateModel(
            name='DTRHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Date of the DTR entry')),
                ('time_in', models.TimeField(help_text='Clock-in time')),
                ('time_out', models.TimeField(blank=True, help_text='Clock-out time', null=True)),
                ('selfie', models.ImageField(help_text='Selfie taken at clock-in', upload_to='selfies/%Y/%m/')),
                ('logout_selfie', models.ImageField(blank=True, help_text='Selfie taken at clock-out', null=True, upload_to='selfies/%Y/%m/')),
                ('hours_rendered', models.FloatField(default=0, help_text='Hours worked')),
                ('notes', models.TextField(blank=True, help_text="Notes about the day's activities")),
                ('confirmation_status', models.CharField(help_text="Status when archived (usually 'rejected')", max_length=20)),
                ('confirmation_remarks', models.TextField(blank=True, help_text="Supervisor's remarks for rejection")),
                ('confirmed_at', models.DateTimeField(blank=True, help_text='When the log was confirmed/rejected', null=True)),
                ('original_created_at', models.DateTimeField(help_text='When the original DTR was created')),
                ('original_updated_at', models.DateTimeField(help_text='When the original DTR was last updated')),
                ('archived_at', models.DateTimeField(auto_now_add=True, help_text='When this entry was moved to history')),
                ('archived_reason', models.CharField(default='resubmission', help_text="Reason for archiving (e.g., 'resubmission')", max_length=50)),
                ('confirmed_by', models.ForeignKey(blank=True, help_text='Supervisor who confirmed/rejected this log', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='confirmed_dtr_history', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(help_text='Student who submitted this DTR', limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.CASCADE, related_name='dtr_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'DTR History',
                'verbose_name_plural': 'DTR Histories',
                'ordering': ['-date', '-archived_at'],
                'indexes': [
                    models.Index(fields=['student', 'date'], name='dtr_dtrhistory_student_date_idx'),
                    models.Index(fields=['confirmation_status'], name='dtr_dtrhistory_confirm_idx'),
                ],
            },
        ),
    ]
