# Generated by Django 3.2.5 on 2021-08-08 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0004_alter_coursesyllabus_number_of_contact_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursesyllabus',
            name='number_of_contact_hours',
            field=models.CharField(max_length=10),
        ),
    ]