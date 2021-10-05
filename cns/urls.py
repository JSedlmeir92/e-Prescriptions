from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='cns-home'),
    # Doctor - Schema
    path('schema/', views.schema_view, name='cns-schema'),
    # Doctor - Credential Definition
    path('cred_def/', views.cred_def_view, name='cns-cred_def'),
    # Doctor - Revocation Registry
    path('rev_reg/', views.rev_reg_view, name='cns-rev_reg'),
    # Doctor - Connection
    path('connection/', views.connection_view, name='cns-connection'),
    # Doctor - Issue Prescription
    path('issue_cred/', views.issue_cred_view, name='cns-issue_cred'),
    # Doctor - Revoke Prescription
    path('revoke_cred/', views.revoke_cred_view, name='cns-revoke_cred'),
    # Doctor - Detailed Overview over a prescription
    path('cred_detail/<int:id>/', views.cred_detail_view, name='cns-cred_detail')
]
