# Generated by Django 5.2.4 on 2025-07-28 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_alter_userprofile_investment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='interest',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
