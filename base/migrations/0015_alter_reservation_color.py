# Generated by Django 5.0.7 on 2024-08-29 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_reservation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='color',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
