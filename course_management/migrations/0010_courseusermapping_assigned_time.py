# Generated by Django 3.2.4 on 2022-02-18 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0009_auto_20220207_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseusermapping',
            name='assigned_time',
            field=models.DateTimeField(null=True),
        ),
    ]
