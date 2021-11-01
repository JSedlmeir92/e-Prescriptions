from django import forms
from .models import Credential, Connection
from django.db.models import Q

class CredentialForm(forms.ModelForm):
    # Creating dropdown list with all the available divisions
    
    connection_id     = forms.ChoiceField(choices=[], widget=[])
    # matricule         = forms.CharField(initial='000000000000', label='Insured person matricule', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    firstname         = forms.CharField(initial='Max', label='Insured person first name', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    lastname          = forms.CharField(initial='Mustermann', label='Insured person last name', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    street = forms.CharField(initial='Musterstraße 1', label='Insured person street address', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    zip_code = forms.CharField(initial='123456', label='Insured person zip code', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    city = forms.CharField(initial='Musterstadt', label='Insured person city', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    # doctor_type       = forms.CharField(initial='Physician', widget=forms.TextInput(attrs={'readonly': 'readonly', 'style': 'width:700px; background-color: #bfbfbf'}))
    # doctor_address    = forms.CharField(initial='Health St. 10', widget=forms.TextInput(attrs={'readonly': 'readonly', 'style': 'width:700px; background-color: #bfbfbf'}))
    # patient_fullname  = forms.CharField(initial='Max Mustermann', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    birthday  = forms.CharField(initial='01.01.2000', label='Birthday', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    expiration_date        = forms.CharField(initial='01.01.2022', label='Expiration', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    # prescription_id  = forms.CharField(label='Id', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    # contractAddress  = forms.CharField(label='ContractAddress', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    # spendingKey      = forms.CharField(label='spendingKey', widget=forms.TextInput(attrs={'style': 'width:700px'}))

    class Meta:
        model = Credential
        fields = [
            # 'matricule',
            'firstname',
            'lastname',
            'birthday',
            'street',
            'zip_code',
            'city',
            'expiration_date'
            # 'prescription_id',
            # 'contractAddress',
            # 'spendingKey'
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