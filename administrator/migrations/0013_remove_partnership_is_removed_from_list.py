# Generated by Django 5.1.4 on 2025-01-24 04:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0012_alter_item_property_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partnership',
            name='is_removed_from_list',
        ),
    ]
