# Generated by Django 3.2.5 on 2021-08-07 16:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursesyllabus',
            name='course_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course_management.courseunits'),
        ),
    ]
