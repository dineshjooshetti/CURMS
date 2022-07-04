# Generated by Django 3.2.4 on 2022-03-07 12:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programs', '0003_programdepartmentmapping_programinstitutemapping'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course_management', '0017_alter_programcategorycountmapping_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramCourseCOPSOMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('co', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_management.courseoutcome')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_management.course')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='programs.programs')),
                ('pso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_management.programspecificoutcome')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'program_course_co_pso_mapping',
            },
        ),
        migrations.CreateModel(
            name='ProgramCourseCOPOMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('co', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_management.courseoutcome')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_management.course')),
                ('po', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_management.programcourseoutcome')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='programs.programs')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'program_course_co_po_mapping',
            },
        ),
    ]
