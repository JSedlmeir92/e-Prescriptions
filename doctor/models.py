from django.db import models
from django.urls import reverse

# Create your models here.
# register model in admin.py
# always run 'python3 manage.py makemigrations' & 'python3 manage.py migrate' after changing sth.

class Credential(models.Model):
    id               = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
    doctor_fullname  = models.CharField(default='Brian McHealthy', max_length=120),
    doctor_type      = models.CharField(default='Physician', max_length=120),
    doctor_address   = models.CharField(default='Hospital St. 15', max_length=120),
    issued           = models.DateField(auto_now_add=True),
    patient_fullname = models.CharField(default='Max Mustermann', max_length=120),
    patient_birthday = models.CharField(default='01.01.2000', max_length=120),
    pharmaceutical          = models.CharField(default='Aspirin', max_length=120),
    number           = models.CharField(default='1', max_length=120),
    expiration       = models.CharField(default='3 months', max_length=120),
    prescription_id  = models.CharField(default='test_id', max_length=120),
    contractAddress  = models.CharField(default='test_address', max_length=120),
    spendingKey      = models.CharField(default='test_spending_key', max_length=120),
    connection_id    = models.CharField(max_length=50)
    rev_id           = models.IntegerField(blank=True, null=True)
    issued           = models.DateField(auto_now=False, auto_now_add=True)
    revoked          = models.BooleanField(default=False)
    thread_id        = models.CharField(max_length=50, blank=True, null=True)
    date_added       = models.DateTimeField(auto_now=False, auto_now_add=True)

    def get_absolute_url(self):
        return reverse('doctor-cred_detail', kwargs={'id': self.id})

class Connection(models.Model):
    alias           = models.CharField(max_length=120)
    invitation_link = models.CharField(max_length=500, blank=True, null=True)
    connection_id   = models.CharField(max_length=50, blank=True, null=True)
    date_added      = models.DateTimeField(auto_now=False, auto_now_add=True)
    state           = models.CharField(max_length=50, blank=True, null=True)