# Generated by Django 3.2.4 on 2022-03-03 12:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0012_courseprerequestiesmapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='programcoursemapping',
            name='course_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course_management.coursecategory'),
        ),
    ]
