# Generated by Django 5.0.7 on 2025-03-07 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0025_category_category_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='category_image',
            new_name='cover',
        ),
        migrations.AlterField(
            model_name='theme',
            name='cover',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='theme/'),
        ),
    ]
