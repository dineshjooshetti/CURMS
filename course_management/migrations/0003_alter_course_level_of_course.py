# Generated by Django 3.2.5 on 2021-08-08 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programs', '0001_initial'),
        ('course_management', '0002_alter_coursesyllabus_course_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='level_of_course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='programs.programlevel'),
        ),
    ]
