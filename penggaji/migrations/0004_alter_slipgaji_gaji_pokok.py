# Generated by Django 5.2.1 on 2025-05-21 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('penggaji', '0003_alter_penggajian_options_penggajian_month_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slipgaji',
            name='gaji_pokok',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
