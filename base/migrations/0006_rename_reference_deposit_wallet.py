# Generated by Django 5.2.4 on 2025-07-17 10:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_userprofile_referal_earning'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deposit',
            old_name='reference',
            new_name='wallet',
        ),
    ]
