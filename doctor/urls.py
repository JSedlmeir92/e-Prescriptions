from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='hr-home'),
    # HR - Schema
    path('schema/', views.schema_view, name='hr-schema'),
    # HR - Credential Definition
    path('cred_def/', views.cred_def_view, name='hr-cred_def'),
    # HR - Revocation Registry
    path('rev_reg/', views.rev_reg_view, name='hr-rev_reg'),
    # HR - Connection
    path('connection/', views.connection_view, name='hr-connection'),
    # HR - Issue Credential
    path('issue_cred/', views.issue_cred_view, name='hr-issue_cred'),
    # HR - Revoke Credential
    path('revoke_cred/', views.revoke_cred_view, name='hr-revoke_cred'),
    path('cred_detail/<int:id>/', views.cred_detail_view, name='hr-cred_detail')
]