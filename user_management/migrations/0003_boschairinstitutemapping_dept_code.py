# Generated by Django 3.2.5 on 2021-08-08 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0002_alter_user_designation'),
    ]

    operations = [
        migrations.AddField(
            model_name='boschairinstitutemapping',
            name='dept_code',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
