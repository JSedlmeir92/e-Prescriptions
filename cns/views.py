from django.shortcuts import render, get_object_or_404, redirect
from .models import Credential, Connection
from .forms import CredentialForm, ConnectionForm

import random
import hashlib
import json
import requests
import time
import os
from pathlib import Path

import base64

from datetime import datetime, date
from dateutil.relativedelta import *
import logging
logger = logging.getLogger(__name__)

FileHandler = open("ip_address_vm", "a+")
ip_address = FileHandler.read()

ip_address = os.getenv('ip_address')
# print(f"ip address: {ip_address}")
# os.system("pwd")
# os.system("export $(grep -v '^#' .env | xargs)")
# print(os.environ)

url = f'http://{ip_address}:6080'
# print(f"url: {url}")

support_revocation = True

ATTRIBUTES = [
                "matricule",
                "firstname",
                "lastname",
                "birthday",
                "street",
                "zip_code",
                "city",
                "date_issued",
                "expiration_date",
            ]

COMMENTS = [
    "The matricule of the insured person",
    "The first name of the insured person",
    "The last name of the insured person",
    "The birthday of the insured person in the format dd.mm.yyyy",
    "The street address of the insured person",
    "The zip code of the insured person",
    "The city address of the insured person",
    "The issuance date of the insurance credential",
    "The expiration date of the insurance credential",
]

def home_view(request):
    return render(request, 'cns/base_cns.html', {'title': 'CNS'})

def connection_view(request):
    form = ConnectionForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = ConnectionForm()
    context = {
        'title': 'Establish Connection (CNS)',
        'form': form
    }
    if request.method == 'POST':
        # Deleting old INVITATIONS
        connections_invitation = requests.get(url + '/connections?initiator=self&state=invitation').json()['results']
        if len(connections_invitation) > 0:
            connection_id = requests.get(url + '/connections?initiator=self&state=invitation').json()['results'][0]["connection_id"]
            requests.delete(url + '/connections/' + connection_id)
        # Generating the new INVITATION
        alias = request.POST.get('alias')
        response = requests.post(url + '/connections/create-invitation?alias=' + alias + '&auto_accept=true').json()
        invitation_link = response['invitation_url']
        connection_id = response['connection_id']
        Connection.objects.filter(id=Connection.objects.latest('date_added').id).update(invitation_link=invitation_link)
        Connection.objects.filter(id=Connection.objects.latest('date_added').id).update(connection_id=connection_id)
        # Generating the QR code
        invitation_splitted = invitation_link.split("=", 1)
        temp = json.loads(base64.b64decode(invitation_splitted[1]))
        # Icon for the wallet app
        temp.update({"imageUrl": "https://www.topaze.lu/files/31525.jpg"})
        temp = base64.b64encode(json.dumps(temp).encode("utf-8")).decode("utf-8")
        invitation_splitted[1] = temp
        invitation_link = "=".join(invitation_splitted)
        # print(invitation_link)
        qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + invitation_link + "&amp;size=600x600"
        context['qr_code'] = qr_code
    return render(request, 'cns/connection.html', context)

def schema_view(request):
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    context = {
        'title': 'Schema'
    }
    if len(created_schema) > 0:
        context['created_schema'] = created_schema[0]
        # context['attributes'] = requests.get(url + '/schemas/' + context['created_schema']).json()['schema']['attrNames']
        # context['attributes'][1], context['attributes'][2], context['attributes'][3], context['attributes'][7], context['attributes'][8], context['attributes'][9], context['attributes'][6], context['attributes'][5], context['attributes'][4], context['attributes'][10], context['attributes'][0] = context['attributes'][0], context['attributes'][1], context['attributes'][2], context['attributes'][3], context['attributes'][4], context['attributes'][5], context['attributes'][6], context['attributes'][7], context['attributes'][8], context['attributes'][9], context['attributes'][10]
        context['attributes'] = []
        for index, _ in enumerate(ATTRIBUTES): #displays the ATTRIBUTES with the describing comments
            context['attributes'].append({"attribute": ATTRIBUTES[index].ljust(30), "comment": COMMENTS[index] + "."})
        print(context)
    else:
        pass
    # Publish a new SCHEMA
    if request.method == 'POST':
        create_schema()
        return redirect('.')
    return render(request, 'cns/schema.html', context)

def create_schema():
    schema = {
            "attributes": ATTRIBUTES,
            "schema_name": "securite sociale",
            "schema_version": "1.0"
        }
    requests.post(url + '/schemas', json=schema)

def cred_def_view(request):
    context = {
        'title': 'Credential Definition'
    }
    # Checks if there are suitable SCHEMAS in the wallet
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = 'There is no suitable schema available. Please go back and publish a new one first.'
    else:
        schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
        # Checks if there are suitable REVOCABLE CREDENTIAL DEFINITIONS in the wallet
        created_credential_definitions_revocable = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) > 0:
            context['created_cred_def_rev'] = created_credential_definitions_revocable[0]
        else:
            # Publish a new CREDENTIAL DEFINITION
            if request.method == 'POST':
                schema_id = created_schema[0]
                credential_definition = {
                    "tag": "CNS",
                    "support_revocation": support_revocation,
                    "schema_id": schema_id
                }
                requests.post(url + '/credential-definitions', json=credential_definition)
                return redirect('.')
    return render(request, 'cns/cred_def.html', context)

def rev_reg_view(request):
    context = {
        'title': 'Revocation Registry'
    }
    # if support_revocation == False:
        # return render(request, 'doctor/rev_reg.html', context)

    # Checks if there are suitable SCHEMA in the wallet
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = 'There is no suitable schema & credential definition available. Please go back and publish both first.'
    else:
        # Checks if there are suitable CREDENTIAL DEFINITIONS in the wallet
        schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
        created_credential_definitions_revocable = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) < 1:
            context['available_cred_def'] = 'There is no suitable credential definition available. Please go back and publish a new one first.'
        else:
            # Checks if there is an active REVOCATION REGISTRY available
            cred_def_id = created_credential_definitions_revocable[0]
            revocation_registry_id = requests.get(url + '/revocation/registries/created?cred_def_id=' + cred_def_id + '&state=active').json()['rev_reg_ids']
            if len(revocation_registry_id) > 0:
                context['rev_reg'] = revocation_registry_id[0]
            else:
                try:
                # Publishes a new REVOCATION REGISTRY
                    if request.method == 'POST':
                        cred_def_id = created_credential_definitions_revocable[0]
                        registry = {
                            "max_cred_num": 1000,
                            "credential_definition_id": cred_def_id
                        }
                        requests.post(url + '/revocation/create-registry', json=registry)
                        return redirect('.')
                except Exception as e:
                        print(e)
    return render(request, 'cns/rev_reg.html', context)

def issue_cred_view(request):
    print("Issuing credential")
    # Updates the STATE of all CONNECTIONS that do not have the state 'active' or 'response'
    update_state = Connection.objects.all()
    for object in update_state:
        connection = requests.get(url + '/connections/' + object.connection_id).status_code
        if connection == 200:
            state = requests.get(url + '/connections/' + object.connection_id).json()['state']
            Connection.objects.filter(id=object.id).update(state=state)
        else:
            Connection.objects.filter(id=object.id).delete()
    form = CredentialForm(request.POST or None)
    context = {
        'title': 'Issue Credential',
        'form': form
    }
    # Checks if there is a suitable SCHEMA
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = True
    else:
        # Checks if there is a suitable CREDENTIAL DEFINITION
        schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
        created_credential_definitions_revocable = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) < 1:
            context['available_cred_def'] = True
        else:
            # Checks if there is a suitable REVOCATION REGISTRY
            cred_def_id = created_credential_definitions_revocable[0]
            revocation_registry_id = requests.get(url + '/revocation/registries/created?cred_def_id=' + cred_def_id + '&state=active').json()['rev_reg_ids']
            if len(revocation_registry_id) < 1:
                context['rev_reg'] = True
            else:
                if form.is_valid():
                    # Sending the data to the patient
                    schema = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']
                    schema_name = schema['name']
                    schema_id = schema['id']
                    schema_version = schema['version']
                    schema_issuer_did = requests.get(url + '/wallet/did/public').json()['result']['did']
                    credential_definition_id = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids'][0]
                    rev_reg_id = requests.get(url + '/revocation/registries/created?cred_def_id=' + credential_definition_id + '&state=active').json()['rev_reg_ids'][0]
                    issuer_did = requests.get(url + '/wallet/did/public').json()['result']['did']
                    connection_id = request.POST.get('connection_id')

                    attributes = [
                        {
                            "name": "matricule",
                            "value": f"{random.randint(10000, 100000)}{request.POST.get('birthday').replace('.', '')}"
                        },
                        {
                            # "mime-type": "image/jpeg",
                            "name": "firstname",
                            "value": request.POST.get('firstname')
                        },
                        {
                            "name": "lastname",
                            "value": request.POST.get('lastname')
                        },
                        {
                            "name": "birthday",
                            "value": request.POST.get('birthday')
                        },
                        {
                            "name": "street",
                            "value": request.POST.get('street')
                        },
                        {
                            "name": "zip_code",
                            "value": request.POST.get('zip_code')
                        },
                        {
                            "name": "city",
                            "value": request.POST.get('city')
                        },
                        {
                            "name": "expiration_date",
                            "value": request.POST.get('expiration_date') #.replace(".", "")
                        },
                        {
                            "name": "date_issued",
                            "value": f"{datetime.now()}"
                        }
                    ]

                    cns_id = "0x" + hashlib.sha256((json.dumps(attributes)).encode('utf-8')).hexdigest()
                    # print("ID: " + prescription_id)
                    # attributes.append(
                    # {
                    #     "name": "cns_id",
                    #     "value": cns_id
                    # })


                    print(attributes)
                    credential = {
                        "schema_name": schema_name,
                        "auto_remove": True,
                        "revoc_reg_id": rev_reg_id,
                        "schema_issuer_did": schema_issuer_did,
                        "schema_version": schema_version,
                        "schema_id": schema_id,
                        "credential_proposal": {
                            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
                            "attributes": attributes,
                        },
                        "credential_def_id": credential_definition_id,
                        "issuer_did": issuer_did,
                        "connection_id": connection_id,
                        "trace": False
                    }
                    print(json.dumps(credential))
                    # Saving the data in the database
                    form.save()
                    form = CredentialForm()
                    issue_cred = requests.post(url + '/issue-credential/send', json=credential)
                        # Updating the object in the database with the thread-id
                        # print(issue_cred)
                        # print(issue_cred.status_code)
                        # print(issue_cred.text)
                else:
                    print("Form invalid")
                    print(form.errors)
    return render(request, 'cns/issue_cred.html', context)

def revoke_cred_view(request):
    # Updates all issued Credentials
    update_credential = Credential.objects.all()
    for object in update_credential:
        credential = requests.get(url + '/issue-credential/records?thread_id=' + str(object.thread_id)).json()['results']
        if len(credential) < 1:
            Credential.objects.filter(id=object.id).delete()
        else:
            pass
    queryset = Credential.objects.filter(revoked=False).order_by('-id')
    context = {
        'title': 'Revoke Credential',
        'object_list': queryset,
        'len': len(queryset)
    }
    return render(request, 'cns/revoke_cred.html', context)

def cred_detail_view(request, id):
    obj = get_object_or_404(Credential, id=id)
    if obj.rev_id == None:
        credential = requests.get(url + '/issue-credential/records?thread_id=' + obj.thread_id).json()['results'][0]
        state = credential['state']
        if state == 'credential_issued':
            rev_id = credential['revocation_id']
            obj.rev_id = rev_id
    if request.method == 'POST':
        revoke= {
            "cred_rev_id" : obj.rev_id,
            "rev_reg_id" : credential['revoc_reg_id'],
            "publish" : "true"
        }
        requests.post(url + '/revocation/revoke', json=revoke)
        obj.revoked = True
        obj.save()
        return redirect('.')
    context = {
        'title': 'Credential Detail',
        'object': obj
    }

    return render(request, 'cns/cred_detail.html', context)
