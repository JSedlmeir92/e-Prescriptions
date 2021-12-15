from django.db.models.query import InstanceCheckMeta
from django.shortcuts import render, get_object_or_404, redirect

from doctor.tables import ConnectionTable, CredentialTable
from .models import Credential, Connection
from .forms import CredentialForm, ConnectionForm
from django.http.response import HttpResponseRedirect
from django.http import HttpResponse 
from django.views.generic import ListView



import hashlib
import json
import requests
import time
import os
from pathlib import Path
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


import base64

from datetime import datetime, date
from dateutil.relativedelta import *
import logging

logger = logging.getLogger(__name__)

ip_address = settings.IP_ADDRESS
port = settings.PORT
url_webapp = f'http://{ip_address}:{port}'

url_doctor_agent = "http://doctor-agent:7080"
url_insurance_agent = "http://insurance-agent:6080"


support_revocation = True

ATTRIBUTES = [
                "doctor_id",
                "doctor_fullname",
                "doctor_type",
                "doctor_phonenumber",
                "patient_insurance_id",
                "patient_insurance_company",
                "patient_fullname",
                "patient_birthday",
                "pharmaceutical",
                "number",
                "extra_information",
                "date_issued",
                "expiration_date",
                "prescription_id",
                "contract_address",
                "spending_key"
            ]

COMMENTS = [
    "The unique ID of the doctor",
    "The full name of the doctor",
    "The exact specialty of the doctor",
    "The phone number of the doctor",
    "The unique Insurance ID of the patient",
    "The patient's insurance company",
    "The full name of the patient",
    "The birth date of the patient in the format yyyy-mm-dd",
    "The pharmaceutical that is prescribed",
    "The number of units of the pharmaceutical",
    "Optional additional information",
    "The issuance date of the prescription",
    "The expiration date of the recipe",
    "The unique id of the prescription to be referred to on the blockchain token",
    "The address of the smart contract in which the doctor creates the prescription token",
    "The private key that allows to spend the token (once only)"
]


##Table
class PrescriptionListView(ListView):
    model = Connection
    table_class = ConnectionTable
    template_name = 'pharmacy/presciption.html'

class CredentialListView(ListView):
    model = Credential
    table_class = CredentialTable
    #template_name = 'pharmacy/rovoke_cred.html'


def home_view(request):
    return render(request, 'doctor/base_doctor.html', {'title': 'Doctor'})



def schema_view(request):
    created_schema = requests.get(url_doctor_agent + '/schemas/created').json()['schema_ids']
    context = {
        'title': 'Schema'
    }
    if len(created_schema) > 0:
        context['created_schema'] = created_schema[0]
        # context['attributes'] = requests.get(url_doctor_agent + '/schemas/' + context['created_schema']).json()['schema']['attrNames']
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
        requests.post(url_doctor_agent + '/schemas', json=schema)
        return redirect('.')
    return render(request, 'doctor/schema.html', context)


def create_schema(): #TODO:Integrating into schema.view and start_demo.py
    schema = {
            "attributes": ATTRIBUTES,
            "schema_name": "ePrescriptionSchema_" + str(time.time())[:10],
            "schema_version": "1.0"
        }
    requests.post(url_doctor_agent + '/schemas', json=schema)

def cred_def_view(request):
    context = {
        'title': 'Credential Definition'
    }
    # Checks if there are suitable SCHEMAS in the wallet
    created_schema = requests.get(url_doctor_agent + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = 'There is no suitable schema available. Please go back and publish a new one first.'
    else:
        schema_name = requests.get(url_doctor_agent + '/schemas/' + created_schema[0]).json()['schema']['name']
        # Checks if there are suitable REVOCABLE CREDENTIAL DEFINITIONS in the wallet
        created_credential_definitions_revocable = requests.get(url_doctor_agent + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
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
                requests.post(url_doctor_agent + '/credential-definitions', json=credential_definition)
                return redirect('.')
    return render(request, 'doctor/cred_def.html', context)

def rev_reg_view(request):
    context = {
        'title': 'Revocation Registry'
    }
    # if support_revocation == False:
        # return render(request, 'doctor/rev_reg.html', context)

    # Checks if there are suitable SCHEMA in the wallet
    created_schema = requests.get(url_doctor_agent + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = 'There is no suitable schema & credential definition available. Please go back and publish both first.'
    else:
        # Checks if there are suitable CREDENTIAL DEFINITIONS in the wallet
        schema_name = requests.get(url_doctor_agent + '/schemas/' + created_schema[0]).json()['schema']['name']
        created_credential_definitions_revocable = requests.get(url_doctor_agent + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) < 1:
            context['available_cred_def'] = 'There is no suitable credential definition available. Please go back and publish a new one first.'
        else:
            # Checks if there is an active REVOCATION REGISTRY available
            cred_def_id = created_credential_definitions_revocable[0]
            revocation_registry_id = requests.get(url_doctor_agent + '/revocation/registries/created?cred_def_id=' + cred_def_id + '&state=active').json()['rev_reg_ids']
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
                        requests.post(url_doctor_agent + '/revocation/create-registry', json=registry)
                        return redirect('.')
                except Exception as e:
                        print(e)
    return render(request, 'doctor/rev_reg.html', context)

#
## Display
#

@csrf_exempt #(Security Excemption): The request send via a form doesn't has to originate from my website and can come from some other domain
def login_view(request):
    context = {
        'title': 'Login',
    }
    # Checks if a SCHEMA and a CREDENTIAL DEFINITION are available.
    created_schema = requests.get(url_doctor_agent + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = "There is no suitable schema & credential definition available. Please go back and publish both first."
    else:
        schema_name = requests.get(url_doctor_agent + '/schemas/' + created_schema[0]).json()['schema']['name']
        cred_def = requests.get(url_doctor_agent + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(cred_def) < 1:
            context['available_cred_def'] = 'There is no suitable credential definition available. Please go back and publish a new one first.'
        else:
            # If an INVITATION is created for a new user, a new session is created and all proof presentations are removed.
            if request.method == 'POST' and 'submit_new_invitation' in request.POST:
                request.session.flush()
                request.session.save()
                proof_records = requests.get(url_doctor_agent + '/present-proof/records').json()['results']
                x = len(proof_records)
                while x > 0:
                    pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
                    requests.delete(url_doctor_agent + '/present-proof/records/' + pres_ex_id)
                    x -= 1
                return redirect('doctor-home')
            # In case the session key is None, the session is stored to get a key
            if not request.session.session_key:
                request.session.save()
            # Checks if there is a CONNECTION with the current session key and a verified proof
            session_key = request.session.session_key
            connections = requests.get(url_doctor_agent + '/connections?alias=' + session_key + '&state=active').json()['results']
            if len(connections) > 0:
                connection_id = connections[0]['connection_id']
                proof = requests.get(url_doctor_agent + '/present-proof/records?connection_id=' + connection_id + '&state=verified').json()['results']
                if (len(proof) > 0):
                    name = proof[0]['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['prescription_id']['raw']
                    context['name'] = name
                else:
                    pass
            else:
                proof_records = requests.get(url_doctor_agent + '/present-proof/records').json()['results']
                x = len(proof_records)
                while x > 0:
                    pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
                    requests.delete(url_doctor_agent + '/present-proof/records/' + pres_ex_id)
                    x -= 1
                connections = requests.get(url_doctor_agent + '/connections').json()['results']
                y = len(connections)
                while y > 0:
                    connection_id = connections[y - 1]["connection_id"]
                    requests.delete(url_doctor_agent + '/connections/' + connection_id)
                    y -= 1
            # Checks if it is necessary to create a new INVITATION QR Code and creates one if necessary
            invitations = requests.get(url_doctor_agent + '/connections?alias=' + session_key + '&state=invitation').json()['results']
            # Creates a new INVITATION, if none exists
            if len(invitations) == 0:
                invitation_link = requests.post(url_doctor_agent + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true&multi_use=true').json()['invitation_url']
                FileHandler = open("doctor/connection_doctor", "w")
                FileHandler.write(invitation_link)
                FileHandler.close()
            elif os.stat("doctor/connection_doctor").st_size == 0:
                connection_id = invitations[0]["connection_id"]
                requests.delete(url_doctor_agent + '/connections/' + connection_id)
                invitation_link = requests.post(url_doctor_agent + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true&multi_use=true').json()['invitation_url']
                FileHandler = open("doctor/connection_doctor", "w")
                FileHandler.write(invitation_link)
                FileHandler.close()
            # Uses the latest created INVITATION, if it has not been used yet
            else:
                FileHandler = open("doctor/connection_doctor", "r")
                invitation_link = FileHandler.read()
                FileHandler.close()
            invitation_splitted = invitation_link.split("=", 1)
            temp = json.loads(base64.b64decode(invitation_splitted[1]))
            # Icon for the wallet app
            temp.update({"imageUrl": "https://cdn.pixabay.com/photo/2016/03/31/20/12/doctor-1295581_960_720.png"})
            temp = base64.b64encode(json.dumps(temp).encode("utf-8")).decode("utf-8")
            invitation_splitted[1] = temp
            invitation_link = "=".join(invitation_splitted)
            qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + invitation_link + "&amp;size=600x600" ##"Connection-based" inivitation
            context['qr_code'] = qr_code
            print(invitation_link)
    return render(request, 'doctor/login.html', context)

def patients_table_view(request):
    table = ConnectionTable(Connection.objects.all())
    return render(request, "doctor/patients.html", {
        "table": table
    })

def patients_detail_view(request, id):
    obj = get_object_or_404(Connection, id=id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            Connection.objects.filter(id=id).delete()
            return redirect('doctor-patients')
    context = {
        'title': 'Prescription Detail',
        'object': obj
    }
    return render(request, 'doctor/patients_detail.html', context)

def patients_delete_item_view(request, id):
    Connection.objects.filter(id=id).delete()
    return redirect('doctor-patients')

#
## Credential issuance
#
def issue_cred_view(request, id):
    # Updates the STATE of all CONNECTIONS that do not have the state 'active' or 'response'
    update_state = Connection.objects.all()
    obj = get_object_or_404(Connection, id=id)
    for object in update_state:
        connection = requests.get(url_doctor_agent + '/connections/' + object.connection_id).status_code
        if connection == 200:
            state = requests.get(url_doctor_agent + '/connections/' + object.connection_id).json()['state']
            Connection.objects.filter(id=object.id).update(connection_state=state)
        else:
            print(object)
            #Connection.objects.filter(id=object.id).delete()
    form = CredentialForm(request.POST or None)
    context = {
        'title': 'Issue Credential',
        'form': form,
        'object': obj
    }
    # Checks if there is a suitable SCHEMA
    created_schema = requests.get(url_doctor_agent + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = True
    else:
        # Checks if there is a suitable CREDENTIAL DEFINITION
        schema_name = requests.get(url_doctor_agent + '/schemas/' + created_schema[0]).json()['schema']['name']
        created_credential_definitions_revocable = requests.get(url_doctor_agent + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) < 1:
            context['available_cred_def'] = True
        else:
            # Checks if there is a suitable REVOCATION REGISTRY
            cred_def_id = created_credential_definitions_revocable[0]
            revocation_registry_id = requests.get(url_doctor_agent + '/revocation/registries/created?cred_def_id=' + cred_def_id + '&state=active').json()['rev_reg_ids']
            if len(revocation_registry_id) < 1:
                context['rev_reg'] = True
            else:
                if form.is_valid():
                    obj = get_object_or_404(Connection, id=id)
                    # Sending the data to the patient
                    schema = requests.get(url_doctor_agent + '/schemas/' + created_schema[0]).json()['schema']
                    schema_name = schema['name']
                    schema_id = schema['id']
                    schema_version = schema['version']
                    schema_issuer_did = requests.get(url_doctor_agent + '/wallet/did/public').json()['result']['did']
                    credential_definition_id = requests.get(url_doctor_agent + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids'][0]
                    rev_reg_id = requests.get(url_doctor_agent + '/revocation/registries/created?cred_def_id=' + credential_definition_id + '&state=active').json()['rev_reg_ids'][0]
                    issuer_did = requests.get(url_doctor_agent + '/wallet/did/public').json()['result']['did']
                    connection_id = obj.connection_id
                    print("Connection_ID: " + connection_id)

                    attributes = [
                        {
                            "name": "doctor_id",
                            "value": '758547302'
                        },
                        {
                            "name": "doctor_fullname",
                            "value": request.POST.get('doctor_fullname')
                        },
                        {
                            "name": "doctor_type",
                            "value": request.POST.get('doctor_type')
                        },
                        {
                            "name": "doctor_phonenumber",
                            "value": request.POST.get('doctor_phonenumber')
                        },
                        {
                            "name": "patient_insurance_id",
                            "value": obj.insurance_id
                        },
                        {
                            "name": "patient_insurance_company",
                            "value": obj.insurance_company
                        },
                        {
                            "name": "patient_fullname",
                            "value": str(obj.firstname + " " + obj.lastname)
                        },
                        {
                            "name": "patient_birthday",
                            "value": obj.birthday
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
                            "name": "extra_information",
                            "value": request.POST.get('extra_information')
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
                    print(attributes)
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
                        issue_cred = requests.post(url_doctor_agent + '/issue-credential/send', json=credential)
                        # Updating the object in the database with the thread-id
                        # print(issue_cred)
                        # print(issue_cred.status_code)
                        # print(issue_cred.text)
                        thread_id = issue_cred.json()['credential_offer_dict']['@id']
                        Credential.objects.filter(id=Credential.objects.latest('date_added').id).update(thread_id=thread_id)
                        context['form'] = form
                        context['name'] = str(obj.firstname + " " + obj.lastname)

                else:
                    print("Form invalid")
                    print(form.errors)
    return render(request, 'doctor/issue_cred.html', context)


#
#Revocation
#
def revoke_cred_view(request):
    # Updates all issued Credentials
    update_credential = Credential.objects.all()
    print(url_doctor_agent)

    for object in update_credential:
        credential = requests.get(url_doctor_agent + '/issue-credential/records?thread_id=' + str(object.thread_id)).json()['results']
        if len(credential) < 1:
            Credential.objects.filter(id=object.id).delete()
        else:
            pass
    queryset = Credential.objects.filter(revoked=False).order_by('-id')
    table = CredentialTable(Credential.objects.all())
    context = {
        'title': 'Revoke Credential',
        'object_list': queryset,
        'len': len(queryset),
        'table': table
    }
    return render(request, 'doctor/revoke_cred.html', context)

def cred_detail_view(request, id):
    obj = get_object_or_404(Credential, id=id)
    if obj.rev_id == None:
        credential = requests.get(url_doctor_agent + '/issue-credential/records?thread_id=' + obj.thread_id).json()['results'][0]
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
        requests.post(url_doctor_agent + '/revocation/revoke', json=revoke)
        obj.revoked = True
        obj.save()
        return redirect('.')
    context = {
        'title': 'Credential Detail',
        'object': obj
    }
    return render(request, 'doctor/cred_detail.html', context)

#
# Webhook
#

@require_POST
@csrf_exempt
def webhook_connection_view(request):
    state = json.loads(request.body)['state']
    print(state)
    if state == 'response': #((state == 'active') or (state == 'response')):
        # Deletes old PROOF requests & presentations
        proof_records = requests.get(url_doctor_agent + '/present-proof/records').json()['results']
        x = len(proof_records)
        # while x > 0:
        #     pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
        #     requests.delete(url_doctor_agent + '/present-proof/records/' + pres_ex_id)
        #     x -= 1
        # Gets the CONNECTION ID (to which the proof should be sent)
        connection_id = requests.get(url_doctor_agent + '/connections').json()['results'][0]['connection_id']
        # Gets the CREDENTIAL DEFINITION ID for the proof of a REVOCABLE credential
        created_schema = requests.get(url_insurance_agent + '/schemas/created').json()['schema_ids']
        schema_name = requests.get(url_insurance_agent + '/schemas/' + created_schema[0]).json()['schema']['name']
        cred_def_id = requests.get(url_insurance_agent + '/credential-definitions/created?schema_name=' + schema_name).json()[
            'credential_definition_ids'][0]
        # Gets the unixstamp of the next day
        # Creates the PROOF REQUEST #TODO: proof-Request als Variable für beide Methoden
        proof_request = {
            "connection_id": connection_id,
            "proof_request":{
                "name": "Proof of Insurance",
                "version": "1.0",
                "requested_attributes": {
                    "health insurance": {
                    "names": [
                        "insurance_id",
                        "firstname",
                        "lastname",
                        "birthday",
                        "street",
                        "zip_code",
                        "city",
                        "date_issued",
                        "expiration_date",
                        "insurance_company"
                    ],
                    "restrictions": [
                        {
                            "cred_def_id": cred_def_id
                        }
                    ]
                    }
                },
                "requested_predicates": {
                },           
                "non_revoked":{
                    "from": 0,
                    "to": round(time.time())
                }
            }
        }
        print(proof_request)
        requests.post(url_doctor_agent + '/present-proof/send-request', json=proof_request)
    else:
        pass
    return HttpResponse()

@require_POST
@csrf_exempt
def webhook_proof_view(request):
    proof = json.loads(request.body)
    if proof['state'] == 'verified':
        attributes = proof['presentation']['requested_proof']['revealed_attr_groups']['health insurance']['values']
        Connection.objects.update_or_create(
            firstname     = attributes['firstname']['raw'],
            lastname      = attributes['lastname']['raw'],
            street          = attributes['street']['raw'],
            zip_code        = attributes['zip_code']['raw'],
            city            = attributes['city']['raw'],
            birthday        = attributes['birthday']['raw'],
            insurance_company = attributes['insurance_company']['raw'],
            insurance_id    = attributes['insurance_id']['raw'],
            connection_id = proof['connection_id']
        )
    return HttpResponse()

@require_POST
@csrf_exempt
def webhook_catch_all_view(request):
    return