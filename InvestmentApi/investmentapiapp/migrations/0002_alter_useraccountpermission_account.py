# Generated by Django 5.1.1 on 2024-09-18 17:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investmentapiapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccountpermission',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_permissions', to='investmentapiapp.investmentaccount'),
        ),
    ]
