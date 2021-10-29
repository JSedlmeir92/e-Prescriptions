from django.urls.conf import include
import django_tables2 as tables
from django_tables2 import TemplateColumn
from .models import Prescription
from django_tables2.utils import A  # alias for Accessor

def custom_row_attrs(**kwargs):
    ##Function specify CSS-classes of the rows
    record = kwargs.get('record', None)
    tr_class = ''

    if record:
        if record.redeemed == True:
            tr_class = 'table-success'
        elif record.valid == False or record.not_spent== False:
            tr_class = 'table-danger'
    return tr_class

class PrescriptionTable(tables.Table):
    more_information = tables.LinkColumn('pharmacy-prescription_detail', args=[A('pk')], text='More information', attrs={'a': {'class': 'btn btn-primary'}})
    delete = tables.LinkColumn('pharmacy-prescription_delete_item', args=[A('pk')], text='Delete', attrs={'a': {'class': 'btn btn-danger'}})
    redeem = TemplateColumn(template_name='pharmacy/tables/overview_redeem_column.html')
    
    class Meta:
        model    = Prescription
        fields  = ("id", "patient_fullname", "pharmaceutical", "number", "valid", "not_spent", 'date_presented', 'redeemed')
        template_name = "django_tables2/bootstrap4.html"
        sequence = ("id", "patient_fullname", "pharmaceutical", "number", 'date_presented', "valid", "not_spent", 'redeemed', 'more_information', 'redeem', 'delete',)
        row_attrs = {'class': custom_row_attrs}