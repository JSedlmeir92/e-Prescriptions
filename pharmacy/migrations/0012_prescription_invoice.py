# Generated by Django 3.2.7 on 2021-11-01 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0011_rename_connection_prescription_connection_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='invoice',
            field=models.BooleanField(default=False),
        ),
    ]