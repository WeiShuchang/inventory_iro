# Generated by Django 5.1.4 on 2025-01-22 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0009_partnership_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnership',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending', max_length=50),
        ),
    ]
