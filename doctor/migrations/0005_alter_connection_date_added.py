# Generated by Django 3.2.7 on 2021-12-15 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0004_rename_conection_state_connection_connection_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, verbose_name='check-in date'),
        ),
    ]
