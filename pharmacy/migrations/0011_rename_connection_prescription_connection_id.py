# Generated by Django 3.2.7 on 2021-11-01 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0010_prescription_connection'),
    ]

    operations = [
        migrations.RenameField(
            model_name='prescription',
            old_name='connection',
            new_name='connection_id',
        ),
    ]