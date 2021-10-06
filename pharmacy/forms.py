from django import forms
from .models import Credential, Connection
from django.db.models import Q

class CredentialForm(forms.ModelForm):
    # Creating dropdown list with all the available divisions
    doctors_choices = [
        ('Mrs Smith', 'Mrs Smith'),
        ('Mr Miller', 'Mr Miller')
    ]

    expiration_choices = [
        ('1', '1 Month'),
        ('3', '3 Months')
    ]

    pharmaceuticals_choices = [
        ('Aspirin', 'Aspirin'),
        ('Xarelto', 'Xarelto')
    ]

    connection_id     = forms.ChoiceField(choices=[], widget=[])
    pharmaceutical         = forms.CharField(initial='Aspirin', label='Insured person first name', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    price          = forms.CharField(initial='9.99', label='Insured person last name', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    prescription_id = forms.CharField(initial='1234567890', label='Insured person street address', widget=forms.TextInput(attrs={'style': 'width:700px'}))

    class Meta:
        model = Credential
        fields = [
            'pharmaceutical',
            'price',
            'prescription_id',
        ] 

    # Updating the dropdown list with all the available connections (which have either the state 'active' or 'response') every time the page loads
    def __init__(self, *args, **kwargs):
        super(CredentialForm, self).__init__(*args, **kwargs)
        queryset = Connection.objects.filter(Q(state='active') | Q(state='response')).order_by('-date_added')
        Available_Connections = []
        for instance in queryset:
            separator = ', '
            infoList = separator.join([str(instance.alias), str(instance.date_added)[:19]])
            Available_Connections.append((instance.connection_id, infoList))
        self.fields['connection_id'] = forms.ChoiceField(choices=Available_Connections, widget=forms.Select(attrs={'style': 'width:700px'}))

class ConnectionForm(forms.ModelForm):
    alias = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'style': 'width:700px'}))
    class Meta:
        model = Connection
        fields = [
            'alias'
        ]