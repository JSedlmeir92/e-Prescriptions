from django.db import models
from django.urls import reverse

# Create your models here.
# register model in admin.py
# always run 'python3 manage.py makemigrations' & 'python3 manage.py migrate' after changing sth.

class Credential(models.Model):
    fullname        = models.CharField(max_length=120)
    company         = models.CharField(max_length=120, default='Electronic Company')
    division        = models.CharField(max_length=120)
    jobtitle        = models.CharField(max_length=120)
    connection_id   = models.CharField(max_length=50)
    rev_id          = models.IntegerField(blank=True, null=True)
    issued          = models.DateField(auto_now=False, auto_now_add=True)
    revoked         = models.BooleanField(default=False)
    thread_id       = models.CharField(max_length=50, blank=True, null=True)
    date_added      = models.DateTimeField(auto_now=False, auto_now_add=True)

    def get_absolute_url(self):
        return reverse('hr-cred_detail', kwargs={'id': self.id})

class Connection(models.Model):
    alias           = models.CharField(max_length=120)
    invitation_link = models.CharField(max_length=500, blank=True, null=True)
    connection_id   = models.CharField(max_length=50, blank=True, null=True)
    date_added      = models.DateTimeField(auto_now=False, auto_now_add=True)
    state           = models.CharField(max_length=50, blank=True, null=True)