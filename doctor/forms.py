from django import forms
from .models import Credential, Connection
from django.db.models import Q

class CredentialForm(forms.ModelForm):
    # Creating dropdown list with all the available divisions
    doctors_choices = [
        ('Lisa Cuddy, M.D.', 'Lisa Cuddy, M.D.'),
        ('Bob Kelsp, M.D.', 'Bob  Kelso, M.D.')
    ]

    expiration_choices = [
        ('1', '1 Month'),
        ('3', '3 Months')
    ]

    pharmaceuticals_choices = [
        ('Aspirin', 'Aspirin'),
        ('Xarelto', 'Xarelto')
    ]

    #connection_id     = forms.ChoiceField(choices=[], widget=[])
    doctor_fullname   = forms.CharField(initial='Mr Smith', label='Doctor Full Name', widget=forms.Select(choices=doctors_choices, attrs={'class': 'form-control'}))
    doctor_type       = forms.CharField(initial='Physician', widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    doctor_phonenumber    = forms.CharField(initial='+49 951 161 161', widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    #patient_fullname  = forms.CharField(initial='Max Mustermann', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    #patient_birthday  = forms.CharField(initial='2000-01-01', label='Patient Birthday', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    pharmaceutical    = forms.CharField(initial='Aspirin', label='Pharmaceutical', widget=forms.Select(choices=pharmaceuticals_choices, attrs={'class': 'form-control'}))
    number            = forms.CharField(initial='1', label='Number', widget=forms.TextInput(attrs={'class': 'form-control'}))
    expiration        = forms.CharField(initial='1 Month', label='Expiration', widget=forms.Select(choices=expiration_choices, attrs={'class': 'form-control'}))
    extra_information = forms.CharField(label='extra_information', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'rows': '2'}))
    # prescription_id  = forms.CharField(label='Id', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    # contractAddress  = forms.CharField(label='ContractAddress', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    # spendingKey      = forms.CharField(label='spendingKey', widget=forms.TextInput(attrs={'style': 'width:700px'}))

    class Meta:
        model = Credential
        fields = [
            #'connection_id',
            'doctor_fullname',
            'doctor_type',
            'doctor_phonenumber',
            #'patient_fullname',
            #'patient_birthday',
            'pharmaceutical',
            'number',
            'expiration',
            'extra_information'
            # 'prescription_id',
            # 'contractAddress',
            # 'spendingKey'
        ]

    # Updating the dropdown list with all the available connections (which have either the state 'active' or 'response') every time the page loads

class ConnectionForm(forms.ModelForm):
    alias = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'style': 'width:700px'}))
    class Meta:
        model = Connection
        fields = [
            'firstname'
        ]