# Generated by Django 3.2.4 on 2022-04-14 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0024_auto_20220413_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='programcategorycountmapping',
            name='label',
            field=models.CharField(max_length=10, null=True),
        ),
    ]