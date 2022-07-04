# Generated by Django 3.2.4 on 2022-03-04 16:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programs', '0003_programdepartmentmapping_programinstitutemapping'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course_management', '0015_alter_programcategorycountmapping_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='programspecificoutcome',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='programs.programs'),
        ),
        migrations.CreateModel(
            name='ProgramCourseOutcome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('po', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_management.course')),
                ('program', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='programs.programs')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'course_program_outcome',
            },
        ),
    ]