# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-04-22 07:35


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tour', '0007_collection'),
    ]

    operations = [
        migrations.AddField(
            model_name='extuser',
            name='address',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='extuser',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
