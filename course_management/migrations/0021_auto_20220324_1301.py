# Generated by Django 3.2.4 on 2022-03-24 13:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programs', '0006_alter_programs_program_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course_management', '0020_auto_20220322_1821'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='course',
        #     name='co_requisites',
        #     field=models.BooleanField(default=0),
        # ),
        # migrations.CreateModel(
        #     name='CourseCorequestiesMapping',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('created', models.DateTimeField(auto_now_add=True, null=True)),
        #         ('corequesti', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_corequesting_mapping', to='course_management.course')),
        #         ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_management.course')),
        #         ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
        #     ],
        #     options={
        #         'db_table': 'course_corequesties_mapping',
        #     },
        # ),
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('basket_name', models.TextField()),
                ('course_count', models.IntegerField()),
                ('credit_count', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_management.coursecategory')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='program_basket_created_by', to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='programs.programs')),
            ],
            options={
                'db_table': 'program_basket',
            },
        ),
    ]
