from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='cns-home'),
    # CNS - Schema
    path('schema/', views.schema_view, name='cns-schema'),
    # CNS - Credential Definition
    path('cred_def/', views.cred_def_view, name='cns-cred_def'),
    # CNS - Revocation Registry
    path('rev_reg/', views.rev_reg_view, name='cns-rev_reg'),
    # CNS - Connection
    path('connection/', views.connection_view, name='cns-connection'),
    # CNS - Issue Credential
    path('issue_cred/', views.issue_cred_view, name='cns-issue_cred'),
    # CNS - Issue Credential
    path('revoke_cred/', views.revoke_cred_view, name='cns-revoke_cred'),
    # CNS - Detailed Overview over a credential
    path('cred_detail/<int:id>/', views.cred_detail_view, name='cns-cred_detail')
]
