from django import forms
from .models import Credential, Connection
from django.db.models import Q

class CredentialForm(forms.ModelForm):
    # Creating dropdown list with all the available divisions
    Doctors = [
        ('A', 'AA'),
        ('B', 'BB'),
        ('C', 'CC'),
        ('D', 'DD')
    ]

    connection_id    = forms.ChoiceField(choices=[], widget=[])
    doctor_fullname  = forms.CharField(label='Full Name', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    doctor_type      = forms.CharField(initial='Mr Smith', widget=forms.TextInput(attrs={'readonly': 'readonly', 'style': 'width:700px; background-color: #bfbfbf'}))
    doctor_address   = forms.CharField(widget=forms.Select(choices=Doctors, attrs={'style': 'width:700px'}))
    patient_fullname = forms.CharField(widget=forms.Select(choices=Doctors, attrs={'style': 'width:700px'}))
    patient_birthday = forms.CharField(label='Patient Birthday', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    medical          = forms.CharField(label='Medical', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    number           = forms.CharField(label='Number', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    expiration       = forms.CharField(label='Expiration', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    prescription_id  = forms.CharField(label='Id', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    contractAddress  = forms.CharField(label='ContractAddress', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    spendingKey      = forms.CharField(label='spendingKey', widget=forms.TextInput(attrs={'style': 'width:700px'}))

    class Meta:
        model = Credential
        fields = [
            'connection_id',
            'doctor_fullname',
            'doctor_type',
            'doctor_address',
            'patient_fullname',
            'patient_birthday',
            'medical',
            'number',
            'expiration',
            'prescription_id',
            'contractAddress',
            'spendingKey'
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