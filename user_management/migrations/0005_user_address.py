# Generated by Django 3.2.5 on 2021-08-12 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0004_alter_boschairinstitutemapping_dept_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.TextField(null=True),
        ),
    ]