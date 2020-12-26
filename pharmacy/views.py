from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import requests
import time
import datetime
import os
import json

url = 'http://0.0.0.0:7080'
url2 = 'http://0.0.0.0:9080'

def home_view(request):
    return render(request, 'work/base_work.html', {'title': 'Work'})

@csrf_exempt
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
                    requests.post(url2 + '/present-proof/records/' + pres_ex_id + '/remove')
                    x -= 1
                return redirect('work-login')
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
                    name = proof[0]['presentation']['requested_proof']['revealed_attrs']['0_name_uuid']['raw']
                    context['name'] = name
                else:
                    pass
            else:
                proof_records = requests.get(url2 + '/present-proof/records').json()['results']
                x = len(proof_records)
                while x > 0:
                    pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
                    requests.post(url2 + '/present-proof/records/' + pres_ex_id + '/remove')
                    x -= 1
                connections = requests.get(url2 + '/connections').json()['results']
                y = len(connections)
                while y > 0:
                    connection_id = connections[y - 1]["connection_id"]
                    requests.post(url2 + '/connections/' + connection_id + '/remove')
                    y -= 1
            # Checks if it is necessary to create a new INVITATION QR Code and creates one if necessary
            invitations = requests.get(url2 + '/connections?alias=' + session_key + '&state=invitation').json()['results']
            # Creates a new INVITATION, if none exists
            if len(invitations) == 0:
                invitation_link = requests.post(url2 + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true').json()['invitation_url']
                FileHandler = open("connection_iam.txt", "w")
                FileHandler.write(invitation_link)
            elif os.stat("connection_iam.txt").st_size == 0:
                connection_id = invitations[0]["connection_id"]
                requests.post(url2 + '/connections/' + connection_id + '/remove')
                invitation_link = requests.post(url2 + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true').json()['invitation_url']
                FileHandler = open("connection_iam.txt", "w")
                FileHandler.write(invitation_link)
            # Uses the latest created INVITATION, if it has not been used yet
            else:
                FileHandler = open("connection_iam.txt", "r")
                invitation_link = FileHandler.read()
            FileHandler.close()
            qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + invitation_link + "&amp;size=600x600"
            context['qr_code'] = qr_code
    return render(request, 'work/login.html', context)

def login_loading_view(request):
    # Deletes old PROOF requests & presentations
    proof_records = requests.get(url2 + '/present-proof/records').json()['results']
    x = len(proof_records)
    while x > 0:
        pres_ex_id = proof_records[x-1]['presentation_exchange_id']
        requests.post(url2 + '/present-proof/records/' + pres_ex_id + '/remove')
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
            "name": "Proof of Division",
            "version": "1.0",
            "requested_attributes": {
                "0_name_uuid": {
                    "name": "Name",
                    "restrictions": [
                        {
                            "cred_def_id": cred_def_id
                        }
                    ]
                },
                "0_company_uuid": {
                    "name": "Company",
                    "restrictions": [
                        {
                            "cred_def_id": cred_def_id
                        }
                    ]
                },
                "0_division_uuid": {
                    "name": "Division",
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
    context = {
        'title': 'Waiting for Proof Presentation',
    }
    return render(request, 'work/login-loading.html', context)

def login_result_view(request):
    x = 0
    while len(requests.get(url2 + '/present-proof/records?state=verified').json()['results']) == 0:
        time.sleep(5)
        # redirect to the login page after 2 minutes of not receiving a proof presentation
        x += 1
        if x > 23:
            return redirect('work-login')
    else:
        proof = requests.get(url2 + '/present-proof/records').json()['results'][0]
        verified = proof['verified']
        context = {
            'title': 'Log In Success',
            'verified': verified
        }
        return render(request, 'work/login-result.html', context)

def logged_in_view(request):
    if request.method == 'POST':
        proof_records = requests.get(url2 + '/present-proof/records').json()['results']
        x = len(proof_records)
        while x > 0:
            pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
            requests.post(url2 + '/present-proof/records/' + pres_ex_id + '/remove')
            x -= 1
        return redirect('work-login')
    proof = requests.get(url2 + '/present-proof/records?state=verified').json()['results']
    if len(proof) > 0:
        name = proof[0]['presentation']['requested_proof']['revealed_attrs']['0_name_uuid']['raw']
        context = {
            'title': 'Logged in',
            'name': name,
            'date': datetime.date.today().strftime('%d - %b - %Y')
        }
        return render(request, 'work/logged_in.html', context)
    else:
        return redirect('work-login')

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
            requests.post(url2 + '/present-proof/records/' + pres_ex_id + '/remove')
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
                "name": "Proof of Division",
                "version": "1.0",
                "requested_attributes": {
                    "0_name_uuid": {
                        "name": "Name",
                        "restrictions": [
                            {
                                "cred_def_id": cred_def_id
                            }
                        ]
                    },
                    "0_company_uuid": {
                        "name": "Company",
                        "restrictions": [
                            {
                                "cred_def_id": cred_def_id
                            }
                        ]
                    },
                    "0_division_uuid": {
                        "name": "Division",
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