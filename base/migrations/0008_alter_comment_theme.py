# Generated by Django 5.0.7 on 2024-08-11 17:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='theme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='base.theme'),
        ),
    ]
