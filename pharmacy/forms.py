from django import forms
from django.db.models import Q
from .models import Prescription

class CredentialForm(forms.ModelForm):
    price         = forms.CharField(label='Total amount of the invoice', widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Prescription
        fields = [
            'invoice'
        ]