# Generated by Django 3.2.4 on 2022-06-24 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0039_courselevels_course_type_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='form_type',
            field=models.IntegerField(null=True),
        ),
    ]
