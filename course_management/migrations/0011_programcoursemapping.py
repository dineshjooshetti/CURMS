# Generated by Django 3.2.4 on 2022-03-02 12:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programs', '0003_programdepartmentmapping_programinstitutemapping'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course_management', '0010_courseusermapping_assigned_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramCourseMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('item_type', models.IntegerField(default=0)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_management.course')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='programs.programs')),
            ],
            options={
                'db_table': 'program_course_mapping',
            },
        ),
    ]
