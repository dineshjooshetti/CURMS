# Generated by Django 3.2.5 on 2021-09-22 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0006_alter_course_course_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='instruction_plan',
            field=models.FileField(max_length=5000, upload_to='media/course/'),
        ),
        migrations.AlterField(
            model_name='course',
            name='instruction_plan_practical',
            field=models.FileField(max_length=5000, null=True, upload_to='media/course/'),
        ),
    ]
