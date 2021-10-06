from django.http.response import HttpResponseRedirect
from pharmacy.models import Prescription

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.generic import ListView
from .tables import PrescriptionTable

import subprocess
import requests
import time
import os
import json
import base64
from datetime import date, datetime
from dateutil.relativedelta import *

ip_address = os.getenv('ip_address')

url = f'http://{ip_address}:7080'
url2 = f'http://{ip_address}:9080'

##Table-stuff
class PrescriptionListView(ListView):
    model = Prescription
    table_class = PrescriptionTable
    template_name = 'pharmacy/presciption.html'



def home_view(request):
    return render(request, 'pharmacy/base_pharmacy.html', {'title': 'Pharmacy'})

@csrf_exempt #(Security Excemption): The request send via a form doesn't has to originate from my website and can come from some other domain
def login_view(request, way = 1): #1 = connectionless proof, 2 = "connectionbased" proof
    context = {
        'title': 'Login',
        'way': way,
    }
    # Checks if a SCHEMA and a CREDENTIAL DEFINITION are available.
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = "There is no suitable schema & credential definition available. Please go back and publish both first."
    else:
        schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
        cred_def = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(cred_def) < 1:
            context['available_cred_def'] = 'There is no suitable credential definition available. Please go back and publish a new one first.'
        else:
            # If an INVITATION is created for a new user, a new session is created and all proof presentations are removed.
            if request.method == 'POST' and 'submit_new_invitation' in request.POST:
                request.session.flush()
                request.session.save()
                proof_records = requests.get(url2 + '/present-proof/records').json()['results']
                x = len(proof_records)
                while x > 0:
                    pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
                    requests.delete(url2 + '/present-proof/records/' + pres_ex_id)
                    x -= 1
                return redirect('pharmacy-connectionless')
            # In case the session key is None, the session is stored to get a key
            if not request.session.session_key:
                request.session.save()
            # Checks if there is a CONNECTION with the current session key and a verified proof
            session_key = request.session.session_key
            connections = requests.get(url2 + '/connections?alias=' + session_key + '&state=active').json()['results']
            if len(connections) > 0:
                connection_id = connections[0]['connection_id']
                proof = requests.get(url2 + '/present-proof/records?connection_id=' + connection_id + '&state=verified').json()['results']
                if (len(proof) > 0):
                    name = proof[0]['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['prescription_id']['raw']
                    context['name'] = name
                else:
                    pass
            else:
                proof_records = requests.get(url2 + '/present-proof/records').json()['results']
                x = len(proof_records)
                while x > 0:
                    pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
                    requests.delete(url2 + '/present-proof/records/' + pres_ex_id)
                    x -= 1
                connections = requests.get(url2 + '/connections').json()['results']
                y = len(connections)
                while y > 0:
                    connection_id = connections[y - 1]["connection_id"]
                    requests.delete(url2 + '/connections/' + connection_id)
                    y -= 1
            # Checks if it is necessary to create a new INVITATION QR Code and creates one if necessary
            invitations = requests.get(url2 + '/connections?alias=' + session_key + '&state=invitation').json()['results']
            # Creates a new INVITATION, if none exists
            if len(invitations) == 0:
                invitation_link = requests.post(url2 + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true&multi_use=true').json()['invitation_url']
                FileHandler = open("pharmacy/connection_pharmacy", "w")
                FileHandler.write(invitation_link)
                FileHandler.close()
            elif os.stat("pharmacy/connection_pharmacy").st_size == 0:
                connection_id = invitations[0]["connection_id"]
                requests.delete(url2 + '/connections/' + connection_id)
                invitation_link = requests.post(url2 + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true&multi_use=true').json()['invitation_url']
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
                qr_code = f"https://api.qrserver.com/v1/create-qr-code/?data=http://{ip_address}:8000/pharmacy/login_url"
            else:
                qr_code = f"https://api.qrserver.com/v1/create-qr-code/?data={invitation_link}&amp;size=600x600" ##"Connection-based" inivitation
            context['qr_code'] = qr_code
    return render(request, 'pharmacy/login.html', context)

def login_connectionless_view(request):
    context = {
        'title': 'Login',

    }
    qr_code = f"https://api.qrserver.com/v1/create-qr-code/?data=http://{ip_address}:8000/pharmacy/login_url"
    context['qr_code'] = qr_code
    return render(request, 'pharmacy/login_connectionless.html', context)

def login_confirmation_view(request, id = 0):
    if id != 0: #Gets the attributes from the database when id is provided
        print(id)
        obj = get_object_or_404(Prescription, id=id)
    else: #Old way
        x = 0
        while len(requests.get(url2 + '/present-proof/records?state=verified').json()['results']) == 0:
            time.sleep(5)
            print("waiting...")
            # redirect to the login page after 2 minutes of not receiving a proof presentation
            x += 1
            if x > 23:
                return redirect('pharmacy-connection_confirmation')
        else:
            proof = requests.get(url2 + '/present-proof/records?state=verified').json()['results'][0]
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


def login_result_view(request, id = 0):
    if id != 0: #Gets the attributes from the database when id is provided
        print(id)
        obj = get_object_or_404(Prescription, id=id)
        verified = obj.valid
        contract_address = obj.contract_address
        prescription_id = obj.prescription_id
        spending_key = obj.spending_key
    else: #Old way
        x = 0
        while len(requests.get(url2 + '/present-proof/records?state=verified').json()['results']) == 0:
            time.sleep(5)
            print("waiting...")
            # redirect to the login page after 2 minutes of not receiving a proof presentation
            x += 1
            if x > 23:
                return redirect('pharmacy-connection')
        else:
            proof = requests.get(url2 + '/present-proof/records?state=verified').json()['results'][0]
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
            print(proof)
            # connection_id =

    print("Spending the prescription")
    print(f"quorum_client/spendPrescription.sh {contract_address} {prescription_id} {spending_key}")
    os.system(f"quorum_client/spendPrescription.sh {contract_address} {prescription_id} {spending_key}")
    result = os.popen("tail -n 1 %s" % "quorum_client/result").read().replace("\n", "")
    result = result == 'true' #Converts result to boolean

    if (result == True and verified == True):
        context = {
            'title': 'Spending Success',
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
        proof_records = requests.get(url2 + '/present-proof/records').json()['results']
        x = len(proof_records)
        while x > 0:
            pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
            requests.delete(url2 + '/present-proof/records/' + pres_ex_id)
            x -= 1
        return redirect('pharmacy-prescription-table')
    proof = requests.get(url2 + '/present-proof/records?state=verified').json()['results']
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
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
    cred_def_id = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()[
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
                    "patient_fullname",
                    "patient_birthday",
                    "doctor_fullname",
                    "doctor_address",
                    "pharmaceutical",
                    "number",
                    "prescription_id",
                    "spending_key",
                    "contract_address"
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
    present_proof = requests.post(url2 + '/present-proof/create-request', json=proof_request).json()
    presentation_request = json.dumps(present_proof["presentation_request"])
    presentation_request = base64.b64encode(presentation_request.encode('utf-8')).decode('ascii')
    invitation = requests.post(url2 + '/connections/create-invitation').json()

    reciepentKeys = invitation["invitation"]["recipientKeys"]
    #verkey = requests.get(url2 + '/wallet/did').json()["results"][0]["verkey"]
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
    invitation_url = f"http://{ip_address}:9000/?d_m={invitation_string}"
    context['invitation'] = invitation_url
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

##Webhooks

@require_POST
@csrf_exempt
def webhook_connection_view(request):
    state = json.loads(request.body)['state']
    print(state)
    if state == 'response': #((state == 'active') or (state == 'response')):
        # Deletes old PROOF requests & presentations
        proof_records = requests.get(url2 + '/present-proof/records').json()['results']
        x = len(proof_records)
        while x > 0:
            pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
            requests.delete(url2 + '/present-proof/records/' + pres_ex_id)
            x -= 1
        # Gets the CONNECTION ID (to which the proof should be sent)
        connection_id = requests.get(url2 + '/connections').json()['results'][0]['connection_id']
        # Gets the CREDENTIAL DEFINITION ID for the proof of a REVOCABLE credential
        created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
        schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
        cred_def_id = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()[
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
                        "patient_fullname",
                        "patient_birthday",
                        "doctor_fullname",
                        "doctor_address",
                        "pharmaceutical",
                        "number",
                        "prescription_id",
                        "spending_key",
                        "contract_address"
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
        requests.post(url2 + '/present-proof/send-request', json=proof_request)
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
        contract_address = str(proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['contract_address']['raw'])
        prescription_id  = str(proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['prescription_id']['raw'])
        spending_key     = str(proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['spending_key']['raw'])
        os.system(f"quorum_client/checkPrescription.sh {contract_address} {prescription_id} {spending_key}")
        not_spent = os.popen("tail -n 1 %s" % "quorum_client/check").read().replace("\n", "") == 'true'
        Prescription.objects.update_or_create(
            prescription_id     = prescription_id,
            defaults={
                "prescription_id"     : prescription_id,
                "patient_fullname"    : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['patient_fullname']['raw'],
                "patient_birthday"    : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['patient_birthday']['raw'],
                "doctor_fullname"     : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['doctor_fullname']['raw'],
                "doctor_address"      : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['doctor_address']['raw'],
                "pharmaceutical"      : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['pharmaceutical']['raw'],
                "number"              : proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['number']['raw'],
                "contract_address"    : contract_address,
                "spending_key"        : spending_key,
                "valid"               : proof['verified'] == "true",
                "not_spent"           : not_spent,
                "date_issued"         : proof['created_at'],
                "date_presented"      : datetime.now() ##TODO:
            }
        )
    return HttpResponse()
