# Generated by Django 5.1.4 on 2025-01-10 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0004_alter_item_responsible_person'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='operating_unit_project',
            field=models.CharField(default='IRO', max_length=200),
        ),
    ]
