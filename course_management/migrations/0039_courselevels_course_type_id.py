# Generated by Django 3.2.4 on 2022-06-24 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0038_remove_courselevels_course_type_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='courselevels',
            name='course_type_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course_management.coursetype'),
        ),
    ]
