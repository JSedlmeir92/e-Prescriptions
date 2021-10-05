from django.contrib import admin
from .models import Credential, Connection

# Register your models here.
admin.site.register(Credential)
admin.site.register(Connection)
