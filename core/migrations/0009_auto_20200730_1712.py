# Generated by Django 3.0.5 on 2020-07-30 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_order_item_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='orders',
            new_name='items',
        ),
    ]
