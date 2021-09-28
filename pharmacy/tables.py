from django.urls.conf import include
import django_tables2 as tables
from .models import Prescription
from django_tables2.utils import A  # alias for Accessor

class PrescriptionTable(tables.Table):
    more_details = tables.LinkColumn('pharmacy-prescription_detail', args=[A('pk')], text='More Information', attrs={'a': {'class': 'btn btn-primary'}})
    redeem = tables.LinkColumn('pharmacy-connection_result', args=[A('pk')], text='Redeen', attrs={'a': {'class': 'btn btn-success'}})
    delete = tables.LinkColumn('pharmacy-prescription_delete_item', args=[A('pk')], text='Delete', attrs={'a': {'class': 'btn btn-danger'}})
    
    class Meta:
        model    = Prescription
        fields  = ("patient_fullname", "pharmaceutical", "number", "revoked", "not_spent", 'date_presented', )
        template_name = "django_tables2/bootstrap4.html"
        sequence = ("patient_fullname", "pharmaceutical", "number", 'date_presented', "revoked", "not_spent", 'more_details', 'redeem', 'delete',)
