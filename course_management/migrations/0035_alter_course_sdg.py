# Generated by Django 3.2.4 on 2022-06-22 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0034_auto_20220622_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='sdg',
            field=models.JSONField(null=True),
        ),
    ]
