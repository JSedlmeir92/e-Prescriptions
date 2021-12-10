from django.shortcuts import render, get_object_or_404, redirect
from .models import Credential, Connection
from .forms import CredentialForm, ConnectionForm


from django.http.response import HttpResponseRedirect

import random
import hashlib
import json
import requests
import time
import os
from pathlib import Path
from django.conf import settings
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

url_pharmacy_agent = "http://pharmacy-agent:9080"
url_insurance_agent = "http://insurance-agent:6080"


support_revocation = True

ATTRIBUTES = [
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
            ]

COMMENTS = [
    "The insurance_id of the insured person",
    "The first name of the insured person",
    "The last name of the insured person",
    "The birthday of the insured person in the format dd.mm.yyyy",
    "The street address of the insured person",
    "The zip code of the insured person",
    "The city address of the insured person",
    "The issuance date of the insurance credential",
    "The expiration date of the insurance credential",
    "The name of the insurance company"
]

def home_view(request):
    return render(request, 'insurance/base_insurance.html', {'title': 'Insurance'})

def connection_view(request):
    form = ConnectionForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = ConnectionForm()
    context = {
        'title': 'Establish Connection (Insurance)',
        'form': form
    }
    if request.method == 'POST':
        # Deleting old INVITATIONS
        connections_invitation = requests.get(url_insurance_agent+ '/connections?initiator=self&state=invitation').json()['results']
        if len(connections_invitation) > 0:
            connection_id = requests.get(url_insurance_agent+ '/connections?initiator=self&state=invitation').json()['results'][0]["connection_id"]
            requests.delete(url_insurance_agent+ '/connections/' + connection_id)
        # Generating the new INVITATION
        alias = request.POST.get('alias')
        response = requests.post(url_insurance_agent+ '/connections/create-invitation?alias=' + alias + '&auto_accept=true').json()
        invitation_link = response['invitation_url']
        connection_id = response['connection_id']
        Connection.objects.filter(id=Connection.objects.latest('date_added').id).update(invitation_link=invitation_link)
        Connection.objects.filter(id=Connection.objects.latest('date_added').id).update(connection_id=connection_id)
        # Generating the QR code
        invitation_splitted = invitation_link.split("=", 1)
        temp = json.loads(base64.b64decode(invitation_splitted[1]))
        # Icon for the wallet app
        temp.update({"imageUrl": "https://empoweredmarketinggroup.com/wp-content/uploads/Suncoast-Health-Insurance-Logo.svg"})
        temp = base64.b64encode(json.dumps(temp).encode("utf-8")).decode("utf-8")
        invitation_splitted[1] = temp
        invitation_link = "=".join(invitation_splitted)
        # print(invitation_link)
        qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + invitation_link + "&amp;size=600x600"
        context['qr_code'] = qr_code
    return render(request, 'insurance/connection.html', context)

def schema_view(request):
    created_schema = requests.get(url_insurance_agent+ '/schemas/created').json()['schema_ids']
    context = {
        'title': 'Schema'
    }
    if len(created_schema) > 0:
        context['created_schema'] = created_schema[0]
        # context['attributes'] = requests.get(url_insurance_agent+ '/schemas/' + context['created_schema']).json()['schema']['attrNames']
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
    return render(request, 'insurance/schema.html', context)

def create_schema():
    schema = {
            "attributes": ATTRIBUTES,
            "schema_name": f"health insurance{random.randint(10000, 100000)}",
            "schema_version": "1.0"
        }
    requests.post(url_insurance_agent+ '/schemas', json=schema)

def cred_def_view(request):
    context = {
        'title': 'Credential Definition'
    }
    # Checks if there are suitable SCHEMAS in the wallet
    created_schema = requests.get(url_insurance_agent+ '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = 'There is no suitable schema available. Please go back and publish a new one first.'
    else:
        schema_name = requests.get(url_insurance_agent+ '/schemas/' + created_schema[0]).json()['schema']['name']
        # Checks if there are suitable REVOCABLE CREDENTIAL DEFINITIONS in the wallet
        created_credential_definitions_revocable = requests.get(url_insurance_agent+ '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) > 0:
            context['created_cred_def_rev'] = created_credential_definitions_revocable[0]
        else:
            # Publish a new CREDENTIAL DEFINITION
            if request.method == 'POST':
                schema_id = created_schema[0]
                credential_definition = {
                    "tag": "Insurance",
                    "support_revocation": support_revocation,
                    "schema_id": schema_id
                }
                requests.post(url_insurance_agent+ '/credential-definitions', json=credential_definition)
                return redirect('.')
    return render(request, 'insurance/cred_def.html', context)

def rev_reg_view(request):
    context = {
        'title': 'Revocation Registry'
    }
    # if support_revocation == False:
        # return render(request, 'doctor/rev_reg.html', context)

    # Checks if there are suitable SCHEMA in the wallet
    created_schema = requests.get(url_insurance_agent+ '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = 'There is no suitable schema & credential definition available. Please go back and publish both first.'
    else:
        # Checks if there are suitable CREDENTIAL DEFINITIONS in the wallet
        schema_name = requests.get(url_insurance_agent+ '/schemas/' + created_schema[0]).json()['schema']['name']
        created_credential_definitions_revocable = requests.get(url_insurance_agent+ '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) < 1:
            context['available_cred_def'] = 'There is no suitable credential definition available. Please go back and publish a new one first.'
        else:
            # Checks if there is an active REVOCATION REGISTRY available
            cred_def_id = created_credential_definitions_revocable[0]
            revocation_registry_id = requests.get(url_insurance_agent+ '/revocation/registries/created?cred_def_id=' + cred_def_id + '&state=active').json()['rev_reg_ids']
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
                        requests.post(url_insurance_agent+ '/revocation/create-registry', json=registry)
                        return redirect('.')
                except Exception as e:
                        print(e)
    return render(request, 'insurance/rev_reg.html', context)

def issue_cred_view(request):
    print("Issuing credential")
    # Updates the STATE of all CONNECTIONS that do not have the state 'active' or 'response'
    update_state = Connection.objects.all()
    for object in update_state:
        connection = requests.get(url_insurance_agent+ '/connections/' + object.connection_id).status_code
        if connection == 200:
            state = requests.get(url_insurance_agent+ '/connections/' + object.connection_id).json()['state']
            Connection.objects.filter(id=object.id).update(state=state)
        else:
            Connection.objects.filter(id=object.id).delete()
    form = CredentialForm(request.POST or None)
    context = {
        'title': 'Issue Credential',
        'form': form
    }
    # Checks if there is a suitable SCHEMA
    created_schema = requests.get(url_insurance_agent+ '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = True
    else:
        # Checks if there is a suitable CREDENTIAL DEFINITION
        schema_name = requests.get(url_insurance_agent+ '/schemas/' + created_schema[0]).json()['schema']['name']
        created_credential_definitions_revocable = requests.get(url_insurance_agent+ '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) < 1:
            context['available_cred_def'] = True
        else:
            # Checks if there is a suitable REVOCATION REGISTRY
            cred_def_id = created_credential_definitions_revocable[0]
            revocation_registry_id = requests.get(url_insurance_agent+ '/revocation/registries/created?cred_def_id=' + cred_def_id + '&state=active').json()['rev_reg_ids']
            if len(revocation_registry_id) < 1:
                context['rev_reg'] = True
            else:
                if form.is_valid():
                    # Sending the data to the patient
                    schema = requests.get(url_insurance_agent+ '/schemas/' + created_schema[0]).json()['schema']
                    schema_name = schema['name']
                    schema_id = schema['id']
                    schema_version = schema['version']
                    schema_issuer_did = requests.get(url_insurance_agent+ '/wallet/did/public').json()['result']['did']
                    credential_definition_id = requests.get(url_insurance_agent+ '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids'][0]
                    rev_reg_id = requests.get(url_insurance_agent+ '/revocation/registries/created?cred_def_id=' + credential_definition_id + '&state=active').json()['rev_reg_ids'][0]
                    issuer_did = requests.get(url_insurance_agent+ '/wallet/did/public').json()['result']['did']
                    connection_id = request.POST.get('connection_id')
                    insurance_id = "O" + str(random.randint(0,999999999))

                    attributes = [
                        {
                            "name": "insurance_id",
                            "value": insurance_id
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
                        },
                        {
                            "name": "insurance_company",
                            "value": "Suncoast Health Insurance"
                        }
                    ]
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
                    issue_cred = requests.post(url_insurance_agent+ '/issue-credential/send', json=credential)
                    context['name'] = str(request.POST.get('firstname') + " " + request.POST.get('lastname'))
                    print(context['name'])
                else:
                    print("")
    return render(request, 'insurance/issue_cred.html', context)

def revoke_cred_view(request):
    # Updates all issued Credentials
    update_credential = Credential.objects.all()
    for object in update_credential:
        credential = requests.get(url_insurance_agent+ '/issue-credential/records?thread_id=' + str(object.thread_id)).json()['results']
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
    return render(request, 'insurance/revoke_cred.html', context)

def cred_detail_view(request, id):
    obj = get_object_or_404(Credential, id=id)
    if obj.rev_id == None:
        credential = requests.get(url_insurance_agent+ '/issue-credential/records?thread_id=' + obj.thread_id).json()['results'][0]
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
        requests.post(url_insurance_agent+ '/revocation/revoke', json=revoke)
        obj.revoked = True
        obj.save()
        return redirect('.')
    context = {
        'title': 'Credential Detail',
        'object': obj
    }

    return render(request, 'insurance/cred_detail.html', context)


def login_view(request):
    context = {
        'title': 'Login',
    }
    # Checks if a SCHEMA and a CREDENTIAL DEFINITION are available.
    qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + url_webapp + "/insurance/login_url"
    context['qr_code'] = qr_code
    return render(request, 'insurance/login.html', context)

def login_result_view(request): ##Checks the validity of the eprescription
    proof_records = requests.get(url_insurance_agent+ '/present-proof/records').json()['results']
    x = len(proof_records)
    print(x)
    while x > 0:
        pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
        requests.delete(url_insurance_agent+ '/present-proof/records/' + pres_ex_id)
        print(x)
        x -= 1
    x = 0
    while len(requests.get(url_insurance_agent+ '/present-proof/records?state=verified').json()['results']) == 0:
        time.sleep(5)
        print("waiting...")
        # redirect to the login page after 2 minutes of not receiving a proof presentation
        x += 1
        if x > 23:
            return redirect('insurance-base')
    proof = requests.get(url_insurance_agent+ '/present-proof/records?state=verified').json()['results'][0]
    insurance_insurance_id = proof['presentation']['requested_proof']['revealed_attr_groups']['insurance']['values']['insurance_id']['raw']
    pharmacy_insurance_id = proof['presentation']['requested_proof']['revealed_attr_groups']['invoice']['values']['insurance_id']['raw']
    if insurance_insurance_id == pharmacy_insurance_id:
        verified = proof['verified'] == 'true'
        print("revoked" + str(verified))
        contract_address = proof['presentation']['requested_proof']['revealed_attr_groups']['invoice']['values']['contract_address']['raw']
        print("contract_address: " + contract_address)
        prescription_id = proof['presentation']['requested_proof']['revealed_attr_groups']['invoice']['values']['invoice_id']['raw']
        print("prescription_id: " + prescription_id)
        spending_key = proof['presentation']['requested_proof']['revealed_attr_groups']['invoice']['values']['spending_key']['raw']
        print("spending_key: " + spending_key)
        os.system(f"quorum_client/spendPrescription.sh {contract_address} {prescription_id} {spending_key}")
        result = os.popen("tail -n 1 %s" % "quorum_client/result").read().replace("\n", "")
        result = result == 'true' #Converts result to boolean
        price = proof['presentation']['requested_proof']['revealed_attr_groups']['invoice']['values']['price']['raw']

        if (result == True and verified == True):
            context = {
                'price': price,
                'verified': "true"
            }
        elif (result == False and verified == True):
            context = {
                'title': 'Invoice already submitted',
                'verified': 'spent'
            }
        elif (result == True and verified == False):
            context = {
                'title': 'Invoice revoked',
                'verified': 'revoked'
            }
        elif (result == False and verified == False):
            context = {
                'title': 'Invoice was revoked and already submitted',
                'verified': 'revoked_and_spent'
            }
        else:
            print("Invalid result: ")
            print(result)
    else:
        print("insurance " + insurance_insurance_id + "pharmacy : " + pharmacy_insurance_id)
        verified = False
        context = {
            'title': 'Invoice was not issued to the person',
            'verified': 'revoked_and_spent'
        }
    return render(request, 'insurance/login-result.html', context)

def login_url_view(request):
    context = {
    }
    # Gets the CREDENTIAL DEFINITION ID for the proof of a REVOCABLE credential
    pharmacy_created_schema = requests.get(url_pharmacy_agent + '/schemas/created').json()['schema_ids']
    pharmacy_schema_name = requests.get(url_pharmacy_agent + '/schemas/' + pharmacy_created_schema[0]).json()['schema']['name']
    pharmacy_cred_def_id = requests.get(url_pharmacy_agent + '/credential-definitions/created?schema_name=' + pharmacy_schema_name).json()[
        'credential_definition_ids'][0]
    insurance_created_schema = requests.get(url_insurance_agent+ '/schemas/created').json()['schema_ids']
    insurance_schema_name = requests.get(url_insurance_agent+ '/schemas/' + insurance_created_schema[0]).json()['schema']['name']
    insurance_cred_def_id = requests.get(url_insurance_agent+ '/credential-definitions/created?schema_name=' + insurance_schema_name).json()[
        'credential_definition_ids'][0]
    print("pharmacy_cred_def_id " + pharmacy_cred_def_id)
    proof_request = {
        "proof_request":{
            "name":"Proof of Receipt",
            "version":"1.0",
            "requested_attributes":{
                "invoice":{
                    "names":[
                        "insurance_id",
                        "pharmaceutical",
                        "quantity",
                        "price",
                        "invoice_id",
                        "contract_address",
                        "spending_key"
                    ],
                    "restrictions":[
                    {
                        "cred_def_id": pharmacy_cred_def_id
                    }
                    ]
                },
                "insurance":{
                    "names":[
                        "insurance_id"
                    ],
                    "restrictions":[
                    {
                        "cred_def_id": insurance_cred_def_id
                    }
                    ]
                }
            },
            "requested_predicates":{
                
            },
            "non_revoked":{
                "from":0,
                "to": round(time.time())
            }
        }
    }
    present_proof = requests.post(url_insurance_agent+ '/present-proof/create-request', json=proof_request).json()
    presentation_request = json.dumps(present_proof["presentation_request"])
    presentation_request = base64.b64encode(presentation_request.encode('utf-8')).decode('ascii')
    invitation = requests.post(url_insurance_agent+ '/connections/create-invitation').json()

    reciepentKeys = invitation["invitation"]["recipientKeys"]
    #verkey = requests.get(url_insurance_agent+ '/wallet/did').json()["results"][0]["verkey"]
    serviceEndPoint = invitation["invitation"]["serviceEndpoint"]
    #routingkeys = invitation["invitation"]["routing_keys"] #TODO: Relevant?
    proof_request_conless = {
        "request_presentations~attach": [
            {
                "@id": "libindy-request-presentation-0",
                "mime-type": "application/json",
                "data": {
                    "base64" : presentation_request
                }
            }
        ],
        "@id" : present_proof["presentation_request_dict"]["@id"],
        "@type": present_proof["presentation_request_dict"]["@type"],
        "~service": {
            "recipientKeys": reciepentKeys,
            "serviceEndpoint": serviceEndPoint,
            "routingKeys": []
        }
    }
    invitation_string = json.dumps(proof_request_conless)
    invitation_string = base64.urlsafe_b64encode(invitation_string.encode('utf-8')).decode('ascii')
    invitation_url = str(url_pharmacy_agent)[:-4] + "7000/?c_i=" + str(invitation_string) ##Changing Agent-Port from API to the Agents' one
    context['invitation'] = invitation_url
    print(invitation_url)
    return HttpResponseRedirect(invitation_url)

@require_POST
@csrf_exempt
def webhook_proof_view(request):
    return

@require_POST
@csrf_exempt
def webhook_catch_all_view(request):
    return