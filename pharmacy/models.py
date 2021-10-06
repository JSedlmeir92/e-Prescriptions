from django.db import models
from django.urls import reverse

class Prescription(models.Model):
    id                  = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    doctor_fullname     = models.CharField(default='Brian McHealthy', max_length=120, null=True)
    doctor_type         = models.CharField(default='Physician', max_length=120)
    doctor_address      = models.CharField(default='Hospital St. 15', max_length=120)
    patient_fullname    = models.CharField(default='Max Mustermann', max_length=120, null=True)
    patient_birthday    = models.CharField(default='01.01.2000', max_length=120)
    pharmaceutical      = models.CharField(default='Aspirin', max_length=120)
    number              = models.CharField(default='1', max_length=120)
    date_issued         = models.CharField(default='01.01.2000', max_length=120)
    contract_address    = models.CharField(default='test_address', max_length=120)
    prescription_id     = models.CharField(default='test_id', max_length=120)
    spending_key        = models.CharField(default='test_spending_key', max_length=120)
    valid               = models.BooleanField(default=False)
    not_spent           = models.BooleanField(default=False)
    date_presented      = models.DateTimeField(auto_now_add=True)
    date_redeemed       = models.DateTimeField(blank=True, null=True)
    redeemed            = models.BooleanField(default=False)

class Credential(models.Model):
    id          = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    pharmaceutical =  models.CharField(default='Aspirin', max_length=120)
    price =  models.CharField(default='12.99', max_length=120)
    prescription_id = models.CharField(default='test_id', max_length=120)

class Connection(models.Model):
    alias           = models.CharField(max_length=120)
    invitation_link = models.CharField(max_length=500, blank=True, null=True)
    connection_id   = models.CharField(max_length=50, blank=True, null=True)
    date_added      = models.DateTimeField(auto_now=False, auto_now_add=True)
    state           = models.CharField(max_length=50, blank=True, null=True)



class Credential(models.Model):
    id          = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    firstname   = models.CharField(default='Max', max_length=120, null=True)
    lastname    = models.CharField(default='Mustermann', max_length=120, null=True)
    birthday    = models.CharField(default='01.01.2000', max_length=120)
    date_issued = models.DateField(auto_now=False, auto_now_add=True)
    expiration_date  = models.CharField(default='01.01.2022', max_length=120)
    date_added       = models.DateTimeField(auto_now=False, auto_now_add=True)

    def get_absolute_url(self):
        return reverse('cns-cred_detail', kwargs={'id': self.id})
