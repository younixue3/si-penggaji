# Generated by Django 5.2.1 on 2025-06-03 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('penggaji', '0004_alter_slipgaji_gaji_pokok'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slipgaji',
            name='gaji_pokok',
            field=models.IntegerField(default=0, help_text='Base salary amount'),
        ),
    ]
