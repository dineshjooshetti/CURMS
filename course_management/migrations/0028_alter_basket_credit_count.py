# Generated by Django 3.2.4 on 2022-05-24 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0027_primarybasketsubbasketmapping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basket',
            name='credit_count',
            field=models.IntegerField(null=True),
        ),
    ]
