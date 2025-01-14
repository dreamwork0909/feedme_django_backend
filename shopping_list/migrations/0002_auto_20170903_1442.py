# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-03 14:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_list', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppinglist',
            name='custom_items',
        ),
        migrations.RemoveField(
            model_name='shoppinglist',
            name='items',
        ),
        migrations.AddField(
            model_name='customitem',
            name='shopping_list',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='custom_items', to='shopping_list.ShoppingList'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='shopping_list',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shopping_list.ShoppingList'),
            preserve_default=False,
        ),
    ]
