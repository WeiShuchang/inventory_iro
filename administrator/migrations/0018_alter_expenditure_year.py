# Generated by Django 5.1.4 on 2025-01-30 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0017_expenditure_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenditure',
            name='year',
            field=models.PositiveIntegerField(default=2024),
        ),
    ]
