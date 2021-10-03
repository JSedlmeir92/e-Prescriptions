from django.db import models

# Create your models here.

class Prescription(models.Model):
    id                  = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    doctor_fullname     = models.CharField(default='Brian McHealthy', max_length=120, null=True)
    doctor_type         = models.CharField(default='Physician', max_length=120)
    doctor_address      = models.CharField(default='Hospital St. 15', max_length=120)
    patient_fullname    = models.CharField(default='Max Mustermann', max_length=120, null=True)
    patient_birthday    = models.CharField(default='01.01.2000', max_length=120)
    pharmaceutical      = models.CharField(default='Aspirin', max_length=120)
    number              = models.CharField(default='1', max_length=120)
    expiration          = models.CharField(default='3 months', max_length=120)
    date_issued         = models.CharField(default='01.01.2000', max_length=120)
    contract_address    = models.CharField(default='test_address', max_length=120)
    prescription_id     = models.CharField(default='test_id', max_length=120)
    spending_key        = models.CharField(default='test_spending_key', max_length=120)
    valid               = models.BooleanField(default=False)
    not_spent           = models.BooleanField(default=False)
    date_presented      = models.DateTimeField(auto_now=False, auto_now_add=True)
    date_spent          = models.DateTimeField(auto_now=True, auto_now_add=False)

