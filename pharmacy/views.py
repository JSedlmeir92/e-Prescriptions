from distutils.command.config import config

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import requests
import time
import datetime
import os
import json
import base64


url = 'http://0.0.0.0:7080'
url2 = 'http://0.0.0.0:9080'

def home_view(request):
    return render(request, 'pharmacy/base_pharmacy.html', {'title': 'Pharmacy'})

@csrf_exempt #(Security Excemption): The request send via a form doesn't has to originate from my website and can come from some other domain
def login_view(request):
    context = {
        'title': 'Login',
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
                return redirect('pharmacy-connection')
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
                FileHandler = open("connection_pharmacy", "w")
                FileHandler.write(invitation_link)
                FileHandler.close()
            elif os.stat("connection_pharmacy").st_size == 0:
                connection_id = invitations[0]["connection_id"]
                requests.delete(url2 + '/connections/' + connection_id)
                invitation_link = requests.post(url2 + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true&multi_use=true').json()['invitation_url']
                FileHandler = open("connection_pharmacy", "w")
                FileHandler.write(invitation_link)
                FileHandler.close()
            # Uses the latest created INVITATION, if it has not been used yet
            else:
                FileHandler = open("connection_pharmacy", "r")
                invitation_link = FileHandler.read()
                FileHandler.close()

            invitation_splitted = invitation_link.split("=", 1)
            temp = json.loads(base64.b64decode(invitation_splitted[1]))
            # Icon for the wallet app
            temp.update({"imageUrl": "https://cdn.pixabay.com/photo/2014/04/03/11/47/pharmacy-312139_960_720.png"})
            temp = base64.b64encode(json.dumps(temp).encode("utf-8")).decode("utf-8")
            invitation_splitted[1] = temp
            invitation_link = "=".join(invitation_splitted)
            print(invitation_link)
            qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + invitation_link + "&amp;size=600x600"
            context['qr_code'] = qr_code
    return render(request, 'pharmacy/login.html', context)

def login_loading_view(request):
    # Deletes old PROOF requests & presentations
    proof_records = requests.get(url2 + '/present-proof/records').json()['results']
    x = len(proof_records)
    while x > 0:
        pres_ex_id = proof_records[x-1]['presentation_exchange_id']
        requests.delete(url2 + '/present-proof/records/' + pres_ex_id)
        x -= 1
    # Gets the CONNECTION ID (to which the proof should be sent)
    connection_id = requests.get(url2 + '/connections').json()['results'][0]['connection_id']
    # Gets the CREDENTIAL DEFINITION ID for the proof of a REVOCABLE credential
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
    cred_def_id = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids'][0]
    # Creates the PROOF REQUEST
    proof_request = {
        "connection_id": connection_id,
        "proof_request": {
            "name": "Proof of Receipt",
            "version": "1.0",
            "requested_attributes": {
                "e-prescription": {
                    "names": [
                        "doctor_fullname",
                        "doctor_address",
                        "pharmaceutical",
                        "number",
                        "prescription_id",
                        "spending_key",
                        "contract_address"
                    ],
                    "non_revoked": {
                        "from": 0,
                        "to": round(time.time())
                    },
                    "restrictions": [
                        {
                            "cred_def_id": cred_def_id
                        }
                    ]
                }
            },
            "requested_predicates": {},
        }
    }
    requests.post(url2 + '/present-proof/send-request', json=proof_request)
    context = {
        'title': 'Waiting for Proof Presentation',
    }
    return render(request, 'pharmacy/login-loading.html', context)

def login_result_view(request):
    x = 0
    while len(requests.get(url2 + '/present-proof/records?state=verified').json()['results']) == 0:
        time.sleep(5)
        print("waiting...")
        # redirect to the login page after 2 minutes of not receiving a proof presentation
        x += 1
        if x > 23:
            return redirect('pharmacy-connection')
    else:
        proof = requests.get(url2 + '/present-proof/records').json()['results'][0]
        # print(proof)
        verified = proof['verified']
        print("verified: " + verified)
        contract_address = proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['contract_address']['raw']
        print("contract_address: " + contract_address)
        prescription_id = proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['prescription_id']['raw']
        print("prescription_id: " + prescription_id)
        spending_key = proof['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['spending_key']['raw']
        print("spending_key: " + spending_key)

        os.system(f"quorum_client/spendPrescription.sh {contract_address} {prescription_id} {spending_key.replace('0x', '')}")
        FileHandler = open("quorum_client/result", "r")
        result = FileHandler.read().replace("\n", "")
        print("result: " + result)
        if (result == "true" and verified == "true"):
            context = {
                'title': 'Spending Success',
                'verified': "true"
            }
        elif (result == "false" and verified == "true"):
            context = {
                'title': 'ePrescription already spent',
                'verified': 'spent'
            }
        elif (result == "true" and verified == "false"):
            context = {
                'title': 'ePrescription revoked',
                'verified': 'revoked'
            }
        elif (result == "false" and verified == "false"):
            context = {
                'title': 'ePrescription revoked and spent',
                'verified': 'revoked_and_spent'
            }
        else:
            print("Invalid result: ")
            print(result)
        return render(request, 'pharmacy/login-result.html', context)

def logged_in_view(request):
    if request.method == 'POST':
        proof_records = requests.get(url2 + '/present-proof/records').json()['results']
        x = len(proof_records)
        while x > 0:
            pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
            requests.delete(url2 + '/present-proof/records/' + pres_ex_id)
            x -= 1
        return redirect('pharmacy-connection')
    proof = requests.get(url2 + '/present-proof/records?state=verified').json()['results']
    if len(proof) > 0:
        # print(proof[0])
        pharmaceutical = proof[0]['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['pharmaceutical']['raw']
        number = proof[0]['presentation']['requested_proof']['revealed_attr_groups']['e-prescription']['values']['number']['raw']
        context = {
            'title': 'Prescription spent',
            'pharmaceutical': pharmaceutical,
            'number': number,
            'date': datetime.date.today().strftime('%d - %b - %Y')
        }
        return render(request, 'pharmacy/logged_in.html', context)
    else:
        return redirect('pharmacy-connection')

@require_POST
@csrf_exempt
def webhook_connection_view(request):
    state = json.loads(request.body)['state']
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
        # Creates the PROOF REQUEST
        proof_request = {
            "connection_id": connection_id,
            "proof_request": {
                            "name": "Proof of Receipt",
            "version": "1.0",
            "requested_attributes": {
                "e-prescription": {
                    "names": [
                        "doctor_fullname",
                        "doctor_address",
                        "pharmaceutical",
                        "number",
                        "prescription_id",
                        "spending_key",
                        "contract_address"
                    ],
                    "non_revoked": {
                        "from": 0,
                        "to": round(time.time())
                    },
                    "restrictions": [
                        {
                            "cred_def_id": cred_def_id
                        }
                    ]
                }
            },
            "requested_predicates": {}
            }
        }
        requests.post(url2 + '/present-proof/send-request', json=proof_request)
    else:
        pass
    return HttpResponse()

@require_POST
@csrf_exempt
def webhook_proof_view(request):
    return HttpResponse()