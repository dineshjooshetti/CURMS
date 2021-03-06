# Generated by Django 3.2.4 on 2022-05-10 14:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course_management', '0026_auto_20220418_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrimaryBasketSubBasketMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='program_sub_basket_created_by', to=settings.AUTH_USER_MODEL)),
                ('primary_basket', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='program_primary_basket', to='course_management.basket')),
                ('sub_basket', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='program_sub_basket', to='course_management.basket')),
            ],
            options={
                'db_table': 'program_primary_basket_sub_basket_mapping',
            },
        ),
    ]
