# Generated by Django 3.2.6 on 2021-08-12 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credential',
            name='doctor_fullname',
            field=models.CharField(default='Brian McHealthy', max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='credential',
            name='patient_fullname',
            field=models.CharField(default='Max Mustermann', max_length=120, null=True),
        ),
    ]
