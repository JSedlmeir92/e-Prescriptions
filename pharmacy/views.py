from django.http.response import HttpResponseRedirect
from pharmacy.models import Prescription

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse 
from django.views.generic import ListView
from .tables import PrescriptionTable
from django.conf import settings
from .forms import CredentialForm

import hashlib
import requests
import time
import os
import json
import base64
from datetime import date, datetime
from dateutil.relativedelta import *
import random

port = settings.PORT
ip_address = settings.IP_ADDRESS

url_pharmacy_agent = f'http://{ip_address}:9080'
url_doctor_agent = f'http://{ip_address}:7080'
url_webapp = f'http://{ip_address}:{port}'


support_revocation = True

ATTRIBUTES = [
                "insurance_id",
                "pharmaceutical",
                "quantity",
                "price",
                "invoice_id",
                "contract_address",
                "spending_key"
            ]

COMMENTS = [
    "The insurance ID of the insurend persion",
    "The sold pharmaceutical",
    "The quantity of the sold pharmaceutical",
    "The price of the sold pharmaceutical",
    "The unique id of the invoice to be referred to on the blockchain token",
    "The address of the smart contract in which the pharamrcy creates the invoice token",
    "The private key that allows to spend the token (once only)"

]

##Table
class PrescriptionListView(ListView):
    model = Prescription
    table_class = PrescriptionTable
    template_name = 'pharmacy/presciption.html'

def home_view(request):
    return render(request, 'pharmacy/base_pharmacy.html', {'title': 'Pharmacy'})

@csrf_exempt 
def login_view(request, way = 1): #1 = connectionless proof, 2 = "connectionbased" proof
    context = {
        'title': 'Login',
        'way': way,
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
                proof_records = requests.get(url_pharmacy_agent + '/present-proof/records').json()['results']
                x = len(proof_records)
                while x > 0:
                    pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
                    requests.delete(url_pharmacy_agent + '/present-proof/records/' + pres_ex_id)
                    x -= 1
                return redirect('pharmacy-connectionless')
            # In case the session key is None, the session is stored to get a key
            if not request.session.session_key:
                request.session.save()
            # Checks if there is a CONNECTION with the current session key and a verified proof
            session_key = request.session.session_key
            connections = requests.get(url_pharmacy_agent + '/connections?alias=' + session_key + '&state=active').json()['results']
            if len(connections) > 0:
                connection_id = connections[0]['connection_id']
                proof = requests.get(url_pharmacy_agent + '/present-proof/records?connection_id=' + connection_id + '&state=verified').json()['results']
                if (len(proof) > 0):
                    name = proof[0]['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['prescription_id']['raw']
                    context['name'] = name
                else:
                    pass
            else:
                proof_records = requests.get(url_pharmacy_agent + '/present-proof/records').json()['results']
                x = len(proof_records)
                while x > 0:
                    pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
                    requests.delete(url_pharmacy_agent + '/present-proof/records/' + pres_ex_id)
                    x -= 1
                connections = requests.get(url_pharmacy_agent + '/connections').json()['results']
                y = len(connections)
                while y > 0:
                    connection_id = connections[y - 1]["connection_id"]
                    requests.delete(url_pharmacy_agent + '/connections/' + connection_id)
                    y -= 1
            # Checks if it is necessary to create a new INVITATION QR Code and creates one if necessary
            invitations = requests.get(url_pharmacy_agent + '/connections?alias=' + session_key + '&state=invitation').json()['results']
            # Creates a new INVITATION, if none exists
            if len(invitations) == 0:
                invitation_link = requests.post(url_pharmacy_agent + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true&multi_use=true').json()['invitation_url']
                FileHandler = open("pharmacy/connection_pharmacy", "w")
                FileHandler.write(invitation_link)
                FileHandler.close()
            elif os.stat("pharmacy/connection_pharmacy").st_size == 0:
                connection_id = invitations[0]["connection_id"]
                requests.delete(url_pharmacy_agent + '/connections/' + connection_id)
                invitation_link = requests.post(url_pharmacy_agent + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true&multi_use=true').json()['invitation_url']
                FileHandler = open("pharmacy/connection_pharmacy", "w")
                FileHandler.write(invitation_link)
                FileHandler.close()
            # Uses the latest created INVITATION, if it has not been used yet
            else:
                FileHandler = open("pharmacy/connection_pharmacy", "r")
                invitation_link = FileHandler.read()
                FileHandler.close()

            invitation_splitted = invitation_link.split("=", 1)
            temp = json.loads(base64.b64decode(invitation_splitted[1]))
            # Icon for the wallet app
            temp.update({"imageUrl": "https://cdn.pixabay.com/photo/2014/04/03/11/47/pharmacy-312139_960_720.png"})
            temp = base64.b64encode(json.dumps(temp).encode("utf-8")).decode("utf-8")
            invitation_splitted[1] = temp
            invitation_link = "=".join(invitation_splitted)
            if way == 1:
                qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + url_webapp + "/pharmacy/login_url"
            else:
                qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + invitation_link + "&amp;size=600x600" ##"Connection-based" inivitation
            context['qr_code'] = qr_code
    return render(request, 'pharmacy/login.html', context)

def login_connectionless_view(request):
    context = {
        'title': 'Login',
    } 
    qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + url_webapp + "/pharmacy/login_url"
    context['qr_code'] = qr_code
    return render(request, 'pharmacy/login_connectionless.html', context)

def login_confirmation_view(request, id = 0):
    if id != 0: #Gets the attributes from the database when id is provided
        print(id)
        obj = get_object_or_404(Prescription, id=id)
    else: #Old way: The app periodically asks the agent if there is a new presented proof. If not the app waits for 5 seconds.
        x = 0
        while len(requests.get(url_pharmacy_agent + '/present-proof/records?state=verified').json()['results']) == 0:
            time.sleep(5)
            print("waiting...")
            # redirect to the login page after 2 minutes of not receiving a proof presentation
            x += 1
            if x > 23:
                return redirect('pharmacy-connection_confirmation')
        else:
            proof = requests.get(url_pharmacy_agent + '/present-proof/records?state=verified').json()['results'][0]
            verified = proof['verified'] == 'true'
            print("revoked" + str(verified))
            contract_address = proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['contract_address']['raw']
            print("contract_address: " + contract_address)
            prescription_id = proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['prescription_id']['raw']
            print("prescription_id: " + prescription_id)
            spending_key = proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['spending_key']['raw']
            print("spending_key: " + spending_key)
            #gets Object.ID from the database
            if Prescription.objects.filter(prescription_id=prescription_id).exists() == False:
                 print("Waiting for webhook...")
                 time.sleep(10)
            id = Prescription.objects.filter(prescription_id=prescription_id).values('id')[0]['id']
            obj = get_object_or_404(Prescription, id=id)
    pharmaceutical = obj.pharmaceutical
    number = obj.number
    patient_fullname = obj.patient_fullname

    context = {
        'title': 'ePrescription check',
        'id': obj.id,
        'pharmaceutical': pharmaceutical,
        'number': number,
        'patient_fullname' : patient_fullname,
        }
    return render(request, 'pharmacy/login-confirmation.html', context)


def login_result_view(request, id = 0): ##Checks the validity of the eprescription
    if id != 0: #Gets the attributes from the database when id is provided
        print(id)
        obj = get_object_or_404(Prescription, id=id)
        verified = obj.valid
        contract_address = obj.contract_address
        prescription_id = obj.prescription_id
        spending_key = obj.spending_key
    else: #Old way
        x = 0
        while len(requests.get(url_pharmacy_agent + '/present-proof/records?state=verified').json()['results']) == 0:
            time.sleep(5)
            print("waiting...")
            # redirect to the login page after 2 minutes of not receiving a proof presentation
            x += 1
            if x > 23:
                return redirect('pharmacy-connection')
        else:
            proof = requests.get(url_pharmacy_agent + '/present-proof/records?state=verified').json()['results'][0]
            verified = proof['verified'] == 'true'
            print("revoked" + str(verified))
            contract_address = proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['contract_address']['raw']
            print("contract_address: " + contract_address)
            prescription_id = proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['prescription_id']['raw']
            print("prescription_id: " + prescription_id)
            spending_key = proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['spending_key']['raw']
            print("spending_key: " + spending_key)
            if Prescription.objects.filter(prescription_id=prescription_id).exists() == False:
                 print("Waiting for webhook...")
                 time.sleep(10)
            id = Prescription.objects.filter(prescription_id=prescription_id).values('id')[0]['id']

    os.system(f"quorum_client/spendPrescription.sh {contract_address} {prescription_id} {spending_key}")
    result = os.popen("tail -n 1 %s" % "quorum_client/result").read().replace("\n", "")
    result = result == 'true' #Converts result to boolean
    
    if (result == True and verified == True):
        context = {
            'title': 'Spending successfull!',
            'verified': "true"
        }
        Prescription.objects.filter(id=id).update(redeemed = True, not_spent = False, date_redeemed = datetime.now())
    elif (result == False and verified == True):
        context = {
            'title': 'ePrescription already spent',
            'verified': 'spent'
        }
        Prescription.objects.filter(id=id).update(not_spent = False)
    elif (result == True and verified == False):
        context = {
            'title': 'ePrescription revoked',
            'verified': 'revoked'
        }
        Prescription.objects.filter(id=id).update(valid = False)
    elif (result == False and verified == False):
        context = {
            'title': 'ePrescription revoked and spent',
            'verified': 'revoked_and_spent'
        }
        Prescription.objects.filter(id=id).update(valid = False, not_spent = False)
    else:
        print("Invalid result: ")
        print(result)
    return render(request, 'pharmacy/login-result.html', context)


def logged_in_view(request): ##No longer in use
    if request.method == 'POST':
        proof_records = requests.get(url_pharmacy_agent + '/present-proof/records').json()['results']
        x = len(proof_records)
        while x > 0:
            pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
            requests.delete(url_pharmacy_agent + '/present-proof/records/' + pres_ex_id)
            x -= 1
        return redirect('pharmacy-prescription-table')
    proof = requests.get(url_pharmacy_agent + '/present-proof/records?state=verified').json()['results']
    if len(proof) > 0:
        # print(proof[0])
        pharmaceutical = proof[0]['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['pharmaceutical']['raw']
        number = proof[0]['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['number']['raw']
        context = {
            'title': 'Prescription spent',
            'pharmaceutical': pharmaceutical,
            'number': number,
            'date': date.today()
        }
        return render(request, 'pharmacy/logged_in.html', context)
    else:
        return redirect('pharmacy-prescription-table')

def login_url_view(request):
    context = {
    }
    # Gets the CREDENTIAL DEFINITION ID for the proof of a REVOCABLE credential
    created_schema = requests.get(url_doctor_agent + '/schemas/created').json()['schema_ids']
    schema_name = requests.get(url_doctor_agent + '/schemas/' + created_schema[0]).json()['schema']['name']
    cred_def_id = requests.get(url_doctor_agent + '/credential-definitions/created?schema_name=' + schema_name).json()[
        'credential_definition_ids'][0]
    print("cred_def_id " + cred_def_id)
    # Gets the unixstamp of the next day
    expiration = date.today() + relativedelta(days=+1, hour=0, minute=0)
    expiration = int(time.mktime(expiration.timetuple()))
    proof_request = {
        "proof_request":{
            "name": "Proof of Receipt",
            "version": "1.0",
            "requested_attributes": {
                "e-prescription": {
                    "names": [
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
                    "prescription_id",
                    "contract_address",
                    "spending_key"
                ],
                "restrictions": [
                    {
                        "cred_def_id": cred_def_id
                    }
                ]
                }
            },
            "requested_predicates": {
                "e-prescription": {
                "name": "expiration_date",
                "p_type": ">=",
                "p_value": expiration,
                "restrictions": [
                    {
                        "cred_def_id": cred_def_id
                    }
                ]
                }
            },
            "non_revoked":{
                "from": 0,
                "to": round(time.time())
            }
        }
    }
    present_proof = requests.post(url_pharmacy_agent + '/present-proof/create-request', json=proof_request).json()
    presentation_request = json.dumps(present_proof["presentation_request"])
    presentation_request = base64.b64encode(presentation_request.encode('utf-8')).decode('ascii')
    invitation = requests.post(url_pharmacy_agent + '/connections/create-invitation').json()

    reciepentKeys = invitation["invitation"]["recipientKeys"]
    #verkey = requests.get(url_pharmacy_agent + '/wallet/did').json()["results"][0]["verkey"]
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

def prescription_table_view(request):
    table = PrescriptionTable(Prescription.objects.all())
    table.order_by = "-date_presented"
    return render(request, "pharmacy/presciption.html", {
        "table": table
    })

def prescription_detail_view(request, id):
    obj = get_object_or_404(Prescription, id=id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            Prescription.objects.filter(id=id).delete()
            return redirect('pharmacy-prescription-table')
    context = {
        'title': 'Prescription Detail',
        'object': obj
    }
    return render(request, 'pharmacy/prescription_detail.html', context)

def prescription_delete_item_view(request, id):
    Prescription.objects.filter(id=id).delete()
    return redirect('pharmacy-prescription-table')

def prescription_check_item_view(request, id):
    #TODO: Check revocation status and token's value
    return redirect('pharmacy-prescription-table')


def schema_view(request):
    created_schema = requests.get(url_pharmacy_agent + '/schemas/created').json()['schema_ids']
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
    return render(request, 'pharmacy/schema.html', context)

def create_schema():
    schema = {
            "attributes": ATTRIBUTES,
            "schema_name": f"health pharmacy{random.randint(10000, 100000)}",
            "schema_version": "1.0"
        }
    requests.post(url_pharmacy_agent + '/schemas', json=schema)

def cred_def_view(request):
    context = {
        'title': 'Credential Definition'
    }
    # Checks if there are suitable SCHEMAS in the wallet
    created_schema = requests.get(url_pharmacy_agent + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = 'There is no suitable schema available. Please go back and publish a new one first.'
    else:
        schema_name = requests.get(url_pharmacy_agent + '/schemas/' + created_schema[0]).json()['schema']['name']
        # Checks if there are suitable REVOCABLE CREDENTIAL DEFINITIONS in the wallet
        created_credential_definitions_revocable = requests.get(url_pharmacy_agent + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) > 0:
            context['created_cred_def_rev'] = created_credential_definitions_revocable[0]
        else:
            # Publish a new CREDENTIAL DEFINITION
            if request.method == 'POST':
                schema_id = created_schema[0]
                credential_definition = {
                    "tag": "Pharmacy",
                    "support_revocation": support_revocation,
                    "schema_id": schema_id
                }
                requests.post(url_pharmacy_agent + '/credential-definitions', json=credential_definition)
                return redirect('.')
    return render(request, 'pharmacy/cred_def.html', context)

def rev_reg_view(request):
    context = {
        'title': 'Revocation Registry'
    }
    created_schema = requests.get(url_pharmacy_agent + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = 'There is no suitable schema & credential definition available. Please go back and publish both first.'
    else:
        # Checks if there are suitable CREDENTIAL DEFINITIONS in the wallet
        schema_name = requests.get(url_pharmacy_agent + '/schemas/' + created_schema[0]).json()['schema']['name']
        created_credential_definitions_revocable = requests.get(url_pharmacy_agent + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) < 1:
            context['available_cred_def'] = 'There is no suitable credential definition available. Please go back and publish a new one first.'
        else:
            # Checks if there is an active REVOCATION REGISTRY available
            cred_def_id = created_credential_definitions_revocable[0]
            revocation_registry_id = requests.get(url_pharmacy_agent + '/revocation/registries/created?cred_def_id=' + cred_def_id + '&state=active').json()['rev_reg_ids']
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
                        requests.post(url_pharmacy_agent + '/revocation/create-registry', json=registry)
                        return redirect('.')
                except Exception as e:
                        print(e)
    return render(request, 'pharmacy/rev_reg.html', context)


def issue_cred_view(request, id):
    print("Issuing credential")
    # Updates the STATE of all CONNECTIONS that do not have the state 'active' or 'response'
    obj = get_object_or_404(Prescription, id=id)

    form = CredentialForm(request.POST or None)
    context = {
        'title': 'Issue Invoice',
        'form': form,
        'object': obj
    }
    # Checks if there is a suitable SCHEMA
    created_schema = requests.get(url_pharmacy_agent + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = True
    else:
        # Checks if there is a suitable CREDENTIAL DEFINITION
        schema_name = requests.get(url_pharmacy_agent + '/schemas/' + created_schema[0]).json()['schema']['name']
        created_credential_definitions_revocable = requests.get(url_pharmacy_agent + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) < 1:
            context['available_cred_def'] = True
        else:
            # Checks if there is a suitable REVOCATION REGISTRY
            cred_def_id = created_credential_definitions_revocable[0]
            revocation_registry_id = requests.get(url_pharmacy_agent + '/revocation/registries/created?cred_def_id=' + cred_def_id + '&state=active').json()['rev_reg_ids']
            if len(revocation_registry_id) < 1:
                context['rev_reg'] = True
            else:
                if form.is_valid():
                    # Sending the data to the patient
                    schema = requests.get(url_pharmacy_agent + '/schemas/' + created_schema[0]).json()['schema']
                    schema_name = schema['name']
                    schema_id = schema['id']
                    schema_version = schema['version']
                    schema_issuer_did = requests.get(url_pharmacy_agent + '/wallet/did/public').json()['result']['did']
                    credential_definition_id = requests.get(url_pharmacy_agent + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids'][0]
                    issuer_did = requests.get(url_pharmacy_agent + '/wallet/did/public').json()['result']['did']
                    connection_id = obj.connection_id
                    invoice_id = "0x" + hashlib.sha256((json.dumps(connection_id)).encode('utf-8')).hexdigest()
                    with open("quorum_client/build/contracts/PrescriptionContract.json", "r") as file:
                        contract = json.load(file)
                    contract_address = contract["networks"]['10']['address']

                    attributes = [
                        {
                            "name": "insurance_id",
                            "value": obj.patient_insurance_id
                        },
                        {
                            "name": "pharmaceutical",
                            "value": obj.pharmaceutical
                        },
                        {
                            "name": "quantity",
                            "value": obj.number
                        },
                        {
                            "name": "contract_address",
                            "value": contract_address
                        },
                        {
                            "name": "invoice_id",
                            "value": invoice_id
                        },
                        {
                            "name": "price",
                            "value": request.POST.get('price')
                        }
                    ]

                    os.system(f"quorum_client/createPrescription.sh {invoice_id}")
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
                        #form.save()
                        #form = CredentialForm()                        
                        issue_cred = requests.post(url_pharmacy_agent + '/issue-credential/send', json=credential)
                        # Updating the object in the database with the thread-id
                        # print(issue_cred)
                        # print(issue_cred.status_code)
                        # print(issue_cred.text)
                        thread_id = issue_cred.json()['credential_offer_dict']['@id']
                        context['form'] = form
                        context['name'] = obj.patient_fullname
        
                else:
                    print("")
    return render(request, 'pharmacy/issue_cred.html', context)

##Webhooks

@require_POST
@csrf_exempt
def webhook_connection_view(request):
    state = json.loads(request.body)['state']
    print(state)
    if state == 'response': #((state == 'active') or (state == 'response')):
        # Deletes old PROOF requests & presentations
        proof_records = requests.get(url_pharmacy_agent + '/present-proof/records').json()['results']
        x = len(proof_records)
        # while x > 0:
        #     pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
        #     requests.delete(url_pharmacy_agent + '/present-proof/records/' + pres_ex_id)
        #     x -= 1
        # Gets the CONNECTION ID (to which the proof should be sent)
        connection_id = requests.get(url_pharmacy_agent + '/connections').json()['results'][0]['connection_id']
        # Gets the CREDENTIAL DEFINITION ID for the proof of a REVOCABLE credential
        created_schema = requests.get(url_doctor_agent + '/schemas/created').json()['schema_ids']
        schema_name = requests.get(url_doctor_agent + '/schemas/' + created_schema[0]).json()['schema']['name']
        cred_def_id = requests.get(url_doctor_agent + '/credential-definitions/created?schema_name=' + schema_name).json()[
            'credential_definition_ids'][0]
        # Gets the unixstamp of the next day
        expiration = date.today() + relativedelta(days=+1, hour=0, minute=0)
        expiration = int(time.mktime(expiration.timetuple()))
        # Creates the PROOF REQUEST #TODO: proof-Request als Variable für beide Methoden
        proof_request = {
            "connection_id": connection_id,
            "proof_request": {
                            "name": "Proof of Receipt",
            "version": "1.0",
            "requested_attributes": {
                "e-prescription": {
                    "names": [
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
                    "prescription_id",
                    "contract_address",
                    "spending_key"
                ],
                "restrictions": [
                    {
                        "cred_def_id": cred_def_id
                    }
                ]
                }
            },
            "requested_predicates": {
                "e-prescription": {
                    "name": "expiration_date",
                    "p_type": ">=", 
                    "p_value": expiration,
                    "restrictions": [
                        {
                            "cred_def_id": cred_def_id
                        }
                    ]
                }
            },
            "non_revoked": {
                "from": 0,
                "to": round(time.time())
                },
            }
        }
        print(proof_records)
        requests.post(url_pharmacy_agent + '/present-proof/send-request', json=proof_request)
    else:
        pass
    return HttpResponse()

@require_POST
@csrf_exempt
def webhook_proof_view(request):
    proof = json.loads(request.body)
    #proof_attributes = proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']
    if proof['state'] == 'verified': 
        print("valid: " + proof['verified'],)
        if "connection_id" in proof:
            connection_id = proof['connection_id']
        else:
            connection_id = "test"
        contract_address = str(proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['contract_address']['raw'])
        prescription_id  = str(proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['prescription_id']['raw'])
        spending_key     = str(proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['spending_key']['raw'])
        if spending_key != None:
            os.system(f"quorum_client/checkPrescription.sh {contract_address} {prescription_id} {spending_key}")
            not_spent = os.popen("tail -n 1 %s" % "quorum_client/check").read().replace("\n", "") == 'true'
            Prescription.objects.update_or_create(
                prescription_id     = prescription_id,
                defaults={ 
                    "prescription_id"     : prescription_id,
                    "doctor_id"           : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['doctor_id']['raw'],
                    "doctor_fullname"     : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['doctor_fullname']['raw'],
                    "doctor_type"         : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['doctor_type']['raw'],
                    "doctor_phonenumber"  : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['doctor_phonenumber']['raw'],
                    "patient_insurance_id"  : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['patient_insurance_id']['raw'],
                    "patient_insurance_company" : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['patient_insurance_company']['raw'],
                    "patient_fullname"    : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['patient_fullname']['raw'],
                    "patient_birthday"    : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['patient_birthday']['raw'],
                    "pharmaceutical"      : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['pharmaceutical']['raw'],
                    "number"              : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['number']['raw'],
                    "extra_information"  : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['extra_information']['raw'],
                    "contract_address"    : contract_address,
                    "spending_key"        : spending_key,
                    "valid"               : proof['verified'] == "true",
                    "not_spent"           : not_spent,
                    "date_issued"         : proof['created_at'],
                    "date_presented"      : datetime.now(),
                    "connection_id"       : connection_id
                }
        )
    return HttpResponse()