# Generated by Django 3.1.2 on 2020-11-27 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=120)),
                ('invitation_link', models.CharField(blank=True, max_length=500, null=True)),
                ('connection_id', models.CharField(blank=True, max_length=50, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('state', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Credential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_fullname', models.CharField(default='Brian McHealthy', max_length=120)),
                ('doctor_type', models.CharField(default='Physician', max_length=120)),
                ('doctor_address', models.CharField(default='Hospital St. 15', max_length=120)),
                ('issued', models.DateField(auto_now_add=True)),
                ('patient_fullname', models.CharField(default='Max Mustermann', max_length=120)),
                ('patient_birthday', models.CharField(default='01.01.2000', max_length=120)),
                ('medical', models.CharField(default='Aspirin', max_length=120)),
                ('number', models.CharField(default='1', max_length=120)),
                ('expiration', models.CharField(default='3 months', max_length=120)),
                ('prescription_id', models.CharField(default='test_id', max_length=120)),
                ('contractAddress', models.CharField(default='test_address', max_length=120)),
                ('spendingKey', models.CharField(default='test_spending_key', max_length=120)),
                ('connection_id', models.CharField(max_length=50)),
                ('rev_id', models.IntegerField(blank=True, null=True)),
                ('revoked', models.BooleanField(default=False)),
                ('thread_id', models.CharField(blank=True, max_length=50, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
