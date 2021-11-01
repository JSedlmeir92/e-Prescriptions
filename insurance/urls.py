from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='insurance-home'),
    # CNS - Schema
    path('schema/', views.schema_view, name='insurance-schema'),
    # CNS - Credential Definition
    path('cred_def/', views.cred_def_view, name='insurance-cred_def'),
    # CNS - Revocation Registry
    path('rev_reg/', views.rev_reg_view, name='insurance-rev_reg'),
    # CNS - Connection
    path('connection/', views.connection_view, name='insurance-connection'),
    # CNS - Issue Credential
    path('issue_cred/', views.issue_cred_view, name='insurance-issue_cred'),
    # CNS - Issue Credential
    path('revoke_cred/', views.revoke_cred_view, name='insurance-revoke_cred'),
    # CNS - Detailed Overview over a credential
    path('cred_detail/<int:id>/', views.cred_detail_view, name='insurance-cred_detail'),
    #Webhook
    path('topic', views.webhook_catch_all_view, name='doctor-webhook-catchall'),

    path('login-result/', views.login_result_view, name='insurance-connection_result'),
    path('login/', views.login_view, name='insurance-login'),
    path('login_url', views.login_url_view, name='insurance-connectionless_url')

]
