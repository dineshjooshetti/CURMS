# Generated by Django 3.2.4 on 2022-06-25 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0040_course_form_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course_management.coursestatuslevels'),
        ),
    ]
