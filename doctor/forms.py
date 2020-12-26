from django import forms
from .models import Credential, Connection
from django.db.models import Q

class CredentialForm(forms.ModelForm):
    # Creating dropdown list with all the available divisions
    Divisions = [
        ('Printer Division', 'Printer Division'),
        ('Camera Division', 'Camera Division'),
        ('Tablet Division', 'Tablet Division'),
        ('Smartphone Division', 'Smartphone Division')
    ]

    connection_id   = forms.ChoiceField(choices=[], widget=[])
    fullname        = forms.CharField(label='Full Name', widget=forms.TextInput(attrs={'style': 'width:700px'}))
    company         = forms.CharField(initial='Electronic Company', widget=forms.TextInput(attrs={'readonly': 'readonly', 'style': 'width:700px; background-color: #bfbfbf'}))
    division        = forms.CharField(widget=forms.Select(choices=Divisions, attrs={'style': 'width:700px'}))
    jobtitle        = forms.CharField(label='Job Title', widget=forms.TextInput(attrs={'style': 'width:700px'}))

    class Meta:
        model = Credential
        fields = [
            'connection_id',
            'fullname',
            'company',
            'division',
            'jobtitle'
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