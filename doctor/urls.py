from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home_view, name='doctor-home'),
    # Doctor - Schema
    path('schema/', views.schema_view, name='doctor-schema'),
    # Doctor - Credential definition
    path('cred_def/', views.cred_def_view, name='doctor-cred_def'),
    path('login/', views.login_view, name='doctor-connection'),
    # Doctor - Revocation registry
    path('rev_reg/', views.rev_reg_view, name='doctor-rev_reg'),
    # Doctor - Connection
    #path('connection/', views.connection_view, name='doctor-connection'),
    #
    path('patients', views.patients_table_view, name='doctor-patients'),
    #Shows more information about an patient
    path('patients/detail/', views.patients_detail_view, name='doctor-patients_detail'),

    path('patients/detail/<int:id>/', views.patients_detail_view, name='doctor-patients_detail'),
    #Deletes the patient from the database, removes the connection and redirects to pharmacy-prescription-table
    path('patients/delete_item/<int:id>', views.patients_delete_item_view, name="doctor-patients_delete_item"),
 
    # Doctor - Issue prescription
    path('issue_cred/<int:id>/', views.issue_cred_view, name='doctor-issue_cred'),
    # Doctor - Revoke prescription
    path('revoke_cred/', views.revoke_cred_view, name='doctor-revoke_cred'),
    # Doctor - Detailed overview of a specific prescription
    path('cred_detail/<int:id>/', views.cred_detail_view, name='doctor-cred_detail'),
    #

    # Webhooks
    #Generates the proof-request after accepting the connection
    path('topic/connections/', views.webhook_connection_view, name='pharmacy-webhook_connection'),
    #Saves the presented proof into the database
    path('topic/present_proof/', views.webhook_proof_view, name='doctor-webhook_proof'),
    #Catches all other webhooks and gives just a simple respond
    re_path(r'^topic/', views.webhook_catch_all_view, name='doctor-webhook-catchall')
]  