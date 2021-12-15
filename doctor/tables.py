from django.urls.conf import include
import django_tables2 as tables
from django_tables2 import TemplateColumn
from .models import Connection, Credential
from django_tables2.utils import A  # alias for Accessor

def custom_row_attrs(**kwargs):
    ##Function specify CSS-classes of the rows
    record = kwargs.get('record', None)
    tr_class = ''

class ConnectionTable(tables.Table):
    #more_information = tables.LinkColumn('doctor-patients_detail', args=[A('pk')], text='More information', attrs={'a': {'class': 'btn btn-primary'}})
    prescribe = tables.LinkColumn('doctor-issue_cred', args=[A('pk')], text='Prescribe', attrs={'a': {'class': 'btn btn-primary'}})
    delete = tables.LinkColumn('doctor-patients_delete_item', args=[A('pk')], text='Delete', attrs={'a': {'class': 'btn btn-danger'}})
    
    class Meta:
        model    = Connection
        fields  = ("id", "firstname", "lastname", "birthday", "date_added")
        template_name = "django_tables2/bootstrap4.html"
        sequence = ("id", "lastname", "firstname", "birthday", "date_added", "prescribe", "delete",)
        row_attrs = {'class': custom_row_attrs}

class CredentialTable(tables.Table):
    more_information = tables.LinkColumn('doctor-cred_detail', args=[A('pk')], text='More information', attrs={'a': {'class': 'btn btn-primary'}})
    
    class Meta:
        model    = Credential
        fields  = ("patient_fullname", "pharmaceutical", "number", "date_issued", "revoked",)
        template_name = "django_tables2/bootstrap4.html"
        sequence = ("patient_fullname", "pharmaceutical", "number", "date_issued", "revoked",)
        row_attrs = {'class': custom_row_attrs}