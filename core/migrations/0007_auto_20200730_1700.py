# Generated by Django 3.0.5 on 2020-07-30 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20200728_1701'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order_item',
            name='user',
        ),
        migrations.AlterField(
            model_name='order_item',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
