from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0002_electionstatus_results_published'),
    ]

    operations = [
        migrations.AddField(
            model_name='electionstatus',
            name='start_time',
            field=models.DateTimeField(blank=True, help_text='Voting opens automatically at this time', null=True),
        ),
        migrations.AddField(
            model_name='electionstatus',
            name='end_time',
            field=models.DateTimeField(blank=True, help_text='Voting closes automatically at this time', null=True),
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=150)),
                ('action', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('vote', 'Vote Cast'), ('register', 'Registration'), ('failed_login', 'Failed Login')], max_length=20)),
                ('detail', models.CharField(blank=True, max_length=255)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='election.student')),
            ],
            options={
                'verbose_name': 'Audit Log Entry',
                'verbose_name_plural': 'Audit Log',
                'ordering': ['-timestamp'],
            },
        ),
    ]
