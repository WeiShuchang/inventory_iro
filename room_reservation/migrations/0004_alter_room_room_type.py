# Generated by Django 5.1.4 on 2025-04-04 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room_reservation', '0003_reservation_cancelled_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_type',
            field=models.CharField(choices=[('Single', 'Single'), ('Double', 'Double'), ('Suite', 'Suite'), ('Hall', 'Hall')], max_length=50),
        ),
    ]
