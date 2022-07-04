# Generated by Django 3.2.4 on 2022-06-29 10:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0044_coursecategory_priority'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('programs', '0007_minorcoreprogrammapping_programcategorycountmapping_programcoursebasket_programcoursecopomapping_pro'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramCourseGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.TextField()),
                ('course_count', models.IntegerField(null=True)),
                ('choice_count', models.IntegerField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course_management.coursecategory')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='programs.programs')),
            ],
            options={
                'db_table': 'program_course_group',
            },
        ),
        migrations.AddField(
            model_name='programcoursebasket',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='programs.programcoursegroup'),
        ),
        migrations.AddField(
            model_name='programcoursemapping',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='programs.programcoursegroup'),
        ),
    ]
