from django.urls import path
from . import views
## Check Read.Me for a more detailed overview

urlpatterns = [
    path('', views.home_view, name='pharmacy-home'),

    ## The old Way; Displays the QR-Code for the proof-invitation AND redirects directly to login-connectionless/
    ##way 1 = connectionless; way 2 = connectionbased
    # And checks if a SCHEMA and a CREDENTIAL DEFINITION are available.
    path('login/', views.login_view, name='pharmacy-connection'),
    path('login/<int:way>', views.login_view, name='pharmacy-connection'),

    ## The new way: Displays a QR-Code for the connectionless proof 
    # (QR-Code points to 'pharmacy-connectionless')
    path('login-connectionless/', views.login_connectionless_view, name='pharmacy-connectionless'),

    ## Redirects to the pharmacy-agent with the required parameters for the connectionless proof 
    path('login_url', views.login_url_view, name='pharmacy-connectionless_url'),

    ## Confirmation page _before_ e-prescription-spending
    ## If no ID is provided: waits until a proof is presented
    path('login-confirmation/', views.login_confirmation_view, name='pharmacy-connection_confirmation'),
    path('login-confirmation/<int:id>', views.login_confirmation_view, name='pharmacy-connection_confirmation'),
    
    # Handles handles the redemption of the ePrescription
    ##If no ID is provided: waits until a proof is presented
    ## If an ID is provided: Redeem the ePrescription 
    # Gets the data from the database
    path('login-result/', views.login_result_view, name='pharmacy-connection_result'),
    path('login-result/<int:id>', views.login_result_view, name='pharmacy-connection_result'),

    ## Presentation of the spent ePrescription --NOT USED
    path('logged-in/', views.logged_in_view, name='pharmacy-logged_in'),
    
    # Pharmarcy - Prescription Overview
    path("prescription/", views.prescription_table_view, name="pharmacy-prescription-table"),
    #Shows more information about an ePrescription
    path('prescription/detail/<int:id>/', views.prescription_detail_view, name='pharmacy-prescription_detail'),
    #Deletes the ePrescription from the database and redirects to pharmacy-prescription-table
    path('prescription/delete_item/<int:id>', views.prescription_delete_item_view, name="pharmacy-prescription_delete_item"),
    #Check Status: Not implemented
    path('prescription/check_item/<int:id>', views.prescription_check_item_view, name="pharmacy-prescription_check_item"), 

    # Insurance - Schema
    path('schema/', views.schema_view, name='pharmacy-schema'),
    # Insurance - Credential Definition
    path('cred_def/', views.cred_def_view, name='pharmacy-cred_def'),
    # Insurance - Revocation Registry
    path('rev_reg', views.rev_reg_view, name='pharmacy-rev_reg'),
    # Insurance - Issue Credential
    path('issue_cred/<int:id>/', views.issue_cred_view, name='pharmacy-issue_cred'),

    ## WEBHOOKS
    #Connectionbased Proof: Creates the proof-request and sends it to the prover
    path('topic/connections/', views.webhook_connection_view, name='pharmacy-webhook_connection'),
    #Saves the presented proof into the database
    path('topic/present_proof/', views.webhook_proof_view, name='pharmacy-webhook_proof'),
]