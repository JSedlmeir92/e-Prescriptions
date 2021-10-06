from logging import StringTemplateStyle
from django.db import models
from django.urls import reverse

# Create your models here.
# register model in admin.py
# always run 'python3 manage.py makemigrations' & 'python3 manage.py migrate' after changing sth.

class Credential(models.Model):
    id          = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    matricule   = models.CharField(default='0000000000000', max_length=120, null=True)
    firstname   = models.CharField(default='Max', max_length=120, null=True)
    lastname    = models.CharField(default='Mustermann', max_length=120, null=True)
    birthday    = models.CharField(default='01.01.2000', max_length=120)
    street      = models.CharField(default='Musterstraße 1', max_length=120)
    zip_code    = models.CharField(default='123456', max_length=120)
    city        = models.CharField(default='Musterstraße', max_length=120)
    date_issued = models.DateField(auto_now=False, auto_now_add=True)
    expiration_date  = models.CharField(default='01.01.2022', max_length=120)
    date_added       = models.DateTimeField(auto_now=False, auto_now_add=True)

    def get_absolute_url(self):
        return reverse('cns-cred_detail', kwargs={'id': self.id})

class Connection(models.Model):
    alias           = models.CharField(max_length=120)
    invitation_link = models.CharField(max_length=500, blank=True, null=True)
    connection_id   = models.CharField(max_length=50, blank=True, null=True)
    date_added      = models.DateTimeField(auto_now=False, auto_now_add=True)
    state           = models.CharField(max_length=50, blank=True, null=True)
