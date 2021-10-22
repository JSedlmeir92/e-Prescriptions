from django.urls.conf import include
import django_tables2 as tables
from django_tables2 import TemplateColumn
from .models import Connection
from django_tables2.utils import A  # alias for Accessor

def custom_row_attrs(**kwargs):
    ##Function specify CSS-classes of the rows
    record = kwargs.get('record', None)
    tr_class = ''

class ConnectionTable(tables.Table):
    more_information = tables.LinkColumn('doctor-patients_detail', args=[A('pk')], text='More information', attrs={'a': {'class': 'btn btn-primary'}})
    prescribe = tables.LinkColumn('doctor-issue_cred', args=[A('pk')], text='Prescribe', attrs={'a': {'class': 'btn btn-primary'}})
    delete = tables.LinkColumn('doctor-patients_delete_item', args=[A('pk')], text='Delete', attrs={'a': {'class': 'btn btn-danger'}})
    
    class Meta:
        model    = Connection
        fields  = ("id", "firstname", "lastname", "birthday",)
        template_name = "django_tables2/bootstrap4.html"
        sequence = ("id", "lastname", "firstname", "birthday", 'more_information', "prescribe", "delete",)
        row_attrs = {'class': custom_row_attrs}