# Generated by Django 3.2.4 on 2022-06-21 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0011_departmentinstitutecodes_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='departmentinstitutecodes',
            name='status',
            field=models.BooleanField(default=1),
        ),
    ]
