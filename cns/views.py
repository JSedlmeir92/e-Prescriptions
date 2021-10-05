from django.shortcuts import render, get_object_or_404, redirect
from .models import Credential, Connection
from .forms import CredentialForm, ConnectionForm

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
print(f"ip address: {ip_address}")
# os.system("pwd")
# os.system("export $(grep -v '^#' .env | xargs)")
print(os.environ)

url = f'http://{ip_address}:7080'
print(f"url: {url}")
support_revocation = True

ATTRIBUTES = [
                "doctor_fullname",
                "doctor_type",
                "doctor_address",
                "patient_fullname",
                "patient_birthday",
                "pharmaceutical",
                "number",
                "date_issued",
                "expiration_date",
                "prescription_id",
                "contract_address",
                "spending_key"
            ]

COMMENTS = [
    "The full name of the doctor",
    "The exact specialty of the doctor",
    "The address of the doctor",
    "The full name of the patient",
    "The birth date of the patient in the format yyyy-mm-dd",
    "The pharmaceutical that is prescribed",
    "The number of units of the pharmaceutical",
    "The issuance date of the prescription",
    "The expiration date of the recipe",
    "The unique id of the prescription to be referred to on the blockchain token",
    "The address of the smart contract in which the doctor creates the prescription token",
    "The private key that allows to spend the token (once only)"
]

def home_view(request):
    return render(request, 'doctor/base_doctor.html', {'title': 'Doctor'})

def connection_view(request):
    form = ConnectionForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = ConnectionForm()
    context = {
        'title': 'Establish Connection (Doctor)',
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
        temp.update({"imageUrl": "https://cdn.pixabay.com/photo/2016/03/31/20/12/doctor-1295581_960_720.png"})
        temp = base64.b64encode(json.dumps(temp).encode("utf-8")).decode("utf-8")
        invitation_splitted[1] = temp
        invitation_link = "=".join(invitation_splitted)
        # print(invitation_link)
        qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + invitation_link + "&amp;size=600x600"
        context['qr_code'] = qr_code
    return render(request, 'doctor/connection.html', context)

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
        pass ##null operation. Nothing happens when the satatement executes.
    # Publish a new SCHEMA
    if request.method == 'POST':
        schema = {
            "attributes": ATTRIBUTES,
            "schema_name": "ePrescriptionSchema_" + str(time.time())[:10],
            "schema_version": "1.0"
        }
        requests.post(url + '/schemas', json=schema)
        return redirect('.')
    return render(request, 'doctor/schema.html', context)

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
                    "tag": "ePrescription",
                    "support_revocation": support_revocation,
                    "schema_id": schema_id
                }
                requests.post(url + '/credential-definitions', json=credential_definition)
                return redirect('.')
    return render(request, 'doctor/cred_def.html', context)

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
    return render(request, 'doctor/rev_reg.html', context)

def issue_cred_view(request):
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
                            # "mime-type": "image/jpeg",
                            "name": "doctor_fullname",
                            "value": request.POST.get('doctor_fullname')
                        },
                        {
                            "name": "doctor_type",
                            "value": request.POST.get('doctor_type')
                        },
                        {
                            "name": "doctor_address",
                            "value": request.POST.get('doctor_address')
                        },
                        {
                            "name": "patient_fullname",
                            "value": request.POST.get('patient_fullname')
                        },
                        {
                            "name": "patient_birthday",
                            "value": request.POST.get('patient_birthday')
                        },
                        {
                            "name": "pharmaceutical",
                            "value": request.POST.get('pharmaceutical')
                        },
                        {
                            "name": "number",
                            "value": request.POST.get('number')
                        },
                        {
                            "name": "date_issued",
                            "value": f"{datetime.now()}"
                        }
                    ]

                    expiration = int(request.POST.get('expiration'))
                    expiration = date.today() + relativedelta(months=+expiration)
                    expiration = time.mktime(expiration.timetuple())
                    attributes.append(
                    {
                        "name": "expiration_date",
                        "value": f"{int(expiration)}"
                    })

                    prescription_id = "0x" + hashlib.sha256((json.dumps(attributes)).encode('utf-8')).hexdigest()
                    # print("ID: " + prescription_id)
                    attributes.append(
                    {
                        "name": "prescription_id",
                        "value": prescription_id
                    })

                    with open("quorum_client/build/contracts/PrescriptionContract.json", "r") as file:
                        contract = json.load(file)

                    contract_address = contract["networks"]['10']['address']
                    # print("contract_address: " + contract_address)
                    attributes.append(
                    {
                        "name": "contract_address",
                        "value": contract_address
                    })

                    os.system(f"quorum_client/createPrescription.sh {prescription_id}")
                    FileHandler = open("quorum_client/spendingKey", "r")
                    spending_key = FileHandler.read().replace("\n", "")
                    # print("Spending key: " + spending_key)
                    if spending_key[0:2] != "0x":
                        print("Is not a hex")
                    else:
                        attributes.append(
                        {
                            "name": "spending_key",
                            "value": spending_key
                        })
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
                        # Saving the data in the database
                        form.save()
                        form = CredentialForm()                        
                        issue_cred = requests.post(url + '/issue-credential/send', json=credential)
                        # Updating the object in the database with the thread-id
                        # print(issue_cred)
                        # print(issue_cred.status_code)
                        # print(issue_cred.text)
                        thread_id = issue_cred.json()['credential_offer_dict']['@id']
                        Credential.objects.filter(id=Credential.objects.latest('date_added').id).update(thread_id=thread_id)
                        context['form'] = form
                        context['name'] = request.POST.get('patient_fullname')

                # else:
                    # print("Form invalid")
                    # print(form.errors)
    return render(request, 'doctor/issue_cred.html', context)

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
    return render(request, 'doctor/revoke_cred.html', context)

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
    return render(request, 'doctor/cred_detail.html', context)