from django.urls.conf import include
import django_tables2 as tables
from .models import Prescription
from django_tables2.utils import A  # alias for Accessor

class PrescriptionTable(tables.Table):
    T1     = '<button type="button" class="btn js-more_information" update-link="{{ record.get_absolute_url_update }}">more information</button>'
    T2     = '<button type="button" class="btn js-delete" delete-link="{{ record.get_absolute_url_delete }}">redeem</button>'
    T3     = '<button type="button" class="btn js-delete" delete-link="{{ record.get_absolute_url_delete }}">delete</button>'
    more_information = tables.TemplateColumn(T1)
    redeem  = tables.TemplateColumn(T2)
    delete = tables.TemplateColumn(T3)
    delete2 = tables.LinkColumn('prescription_delete_item', args=[A('delete-id')], attrs={'a': {'class': 'btn'}})
    edit_entries = tables.TemplateColumn('<a href="{% url \'prescription_detail\' record.id %}">Edit</a>')
    

    
    class Meta:
        model    = Prescription
        fields  = ("patient_fullname", "pharmaceutical", "number", "revoked", "spent", 'date_presented', )
        template_name = "django_tables2/bootstrap4.html"
        sequence = ("patient_fullname", "pharmaceutical", "number", 'date_presented', "revoked", "spent", 'more_information', 'redeem', 'delete', 'delete2')
