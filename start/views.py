from django.shortcuts import render, redirect
from doctor.models import Connection, Credential

import requests

url = 'http://0.0.0.0:7080'
url2 = 'http://0.0.0.0:9080'

def remove_connections_agent_1():
    Connection.objects.all().delete()
    connections = requests.get(url + '/connections').json()['results']
    x = len(connections)
    while x > 0:
        connection_id = connections[x-1]["connection_id"]
        requests.delete(url + '/connections/' + connection_id)
        x -= 1

def remove_connections_agent_2():
    connections = requests.get(url2 + '/connections').json()['results']
    y = len(connections)
    while y > 0:
        connection_id = connections[y-1]["connection_id"]
        requests.delete(url2 + '/connections/' + connection_id)
        y -= 1

def remove_credentials_agent_1():
    Credential.objects.all().delete()
    issue_credential = requests.get(url + '/issue-credential/records').json()['results']
    x = len(issue_credential)
    while x > 0:
        credential_exchange_id = issue_credential[x-1]['credential_exchange_id']
        requests.delete(url + '/issue-credential/records/' + credential_exchange_id)
        x -= 1

def remove_credentials_agent_2():
    issue_credential = requests.get(url2 + '/issue-credential/records').json()['results']
    y = len(issue_credential)
    while y > 0:
        credential_exchange_id = issue_credential[y-1]['credential_exchange_id']
        requests.delete(url2 + '/issue-credential/records/' + credential_exchange_id)
        y -= 1

def remove_proofs_agent_1():
    proof_records = requests.get(url + '/present-proof/records').json()['results']
    x = len(proof_records)
    while x > 0:
        presentation_exchange_id = proof_records[x-1]['presentation_exchange_id']
        requests.delete(url + '/present-proof/records/' + presentation_exchange_id)
        x -= 1

def remove_proofs_agent_2():
    proof_records = requests.get(url2 + '/present-proof/records').json()['results']
    y = len(proof_records)
    while y > 0:
        presentation_exchange_id = proof_records[y-1]['presentation_exchange_id']
        requests.delete(url2 + '/present-proof/records/' + presentation_exchange_id)
        y -= 1

def home_view(request):
    context = {
        'title': 'Start'
    }
    return render(request, 'start/start-home.html', context)

def manage_agent_view(request):
    context = {
        'title': 'Manage Agents',
        'connections_quantity'      : len(requests.get(url + '/connections').json()['results']) - len(requests.get(url + '/connections?state=invitation').json()['results']),
        'connections_quantity2'     : len(requests.get(url2 + '/connections').json()['results']) - len(requests.get(url2 + '/connections?state=invitation').json()['results']),
        'credential_quantity'       : len(requests.get(url + '/issue-credential/records').json()['results']),
        'credential_quantity2'      : len(requests.get(url2 + '/issue-credential/records').json()['results']),
        'proof_quantity'            : len(requests.get(url + '/present-proof/records').json()['results']),
        'proof_quantity2'           : len(requests.get(url2 + '/present-proof/records').json()['results']),
        'connections_invitation'    : len(requests.get(url + '/connections?state=invitation').json()['results']),
        'connections_invitation2'   : len(requests.get(url2 + '/connections?state=invitation').json()['results'])
    }
    return render(request, 'start/manage_agent.html', context)

def remove_connection_1(request):
    remove_connections_agent_1()
    return redirect('..')

def remove_connection_2(request):
    remove_connections_agent_2()
    return redirect('..')

def remove_credential_1(request):
    remove_credentials_agent_1()
    return redirect('..')

def remove_credential_2(request):
    remove_credentials_agent_2()
    return redirect('..')

def remove_proof_1(request):
    remove_proofs_agent_1()
    return redirect('..')

def remove_proof_2(request):
    remove_proofs_agent_2()
    return redirect('..')

def remove_invitation_1(request):
    Connection.objects.filter(state='invitation').delete()
    connections_invitation = requests.get(url + '/connections?initiator=self&state=invitation').json()['results']
    if len(connections_invitation) > 0:
        connection_id = requests.get(url + '/connections?initiator=self&state=invitation').json()['results'][0]["connection_id"]
        requests.delete(url + '/connections/' + connection_id)
    else:
        pass
    return redirect('..')

def remove_invitation_2(request):
    connections_invitation = requests.get(url2 + '/connections?initiator=self&state=invitation').json()['results']
    if len(connections_invitation) > 0:
        connection_id = requests.get(url2 + '/connections?initiator=self&state=invitation').json()['results'][0]["connection_id"]
        requests.delete(url2 + '/connections/' + connection_id)
        print("connection id: " + connection_id)
    else:
        pass
    return redirect('..')

def reset_agents(request):
    # Deleting all PROOFS of Agent 1 (Doctor)
    remove_proofs_agent_1()
    # Deleting all PROOFS of Agent 2 (Pharmacy)
    remove_proofs_agent_2()
    # Deleting all CREDENTIALS of Agent 1 (Doctor)
    remove_credentials_agent_1()
    # Deleting all CREDENTIALS of Agent 2 (Pharmacy)
    remove_credentials_agent_2()
    # Deleting all CONNECTIONS & INVITATIONS of Agent 1 (Doctor)
    remove_connections_agent_1()
    # Deleting all CONNECTIONS & INVITATIONS of Agent 2 (Pharmacy)
    remove_connections_agent_2()
    return redirect('.')
