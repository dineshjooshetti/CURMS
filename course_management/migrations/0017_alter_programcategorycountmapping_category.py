# Generated by Django 3.2.4 on 2022-03-07 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_management', '0016_auto_20220304_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programcategorycountmapping',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course_management.coursecategory'),
        ),
    ]