from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home_view, name='insurance-home'),
    # Insurance - Schema
    path('schema/', views.schema_view, name='insurance-schema'),
    # Insurance - Credential Definition
    path('cred_def/', views.cred_def_view, name='insurance-cred_def'),
    # Insurance - Revocation Registry
    path('rev_reg/', views.rev_reg_view, name='insurance-rev_reg'),
    # Insurance - Connection
    path('connection/', views.connection_view, name='insurance-connection'),
    # Insurance - Issue Credential
    path('issue_cred/', views.issue_cred_view, name='insurance-issue_cred'),
    # Insurance - Issue Credential
    path('revoke_cred/', views.revoke_cred_view, name='insurance-revoke_cred'),
    # Insurance - Detailed Overview over a credential
    path('cred_detail/<int:id>/', views.cred_detail_view, name='insurance-cred_detail'),
    #Webhook

    path('login-result/', views.login_result_view, name='insurance-connection_result'),
    path('login/', views.login_view, name='insurance-login'),
    path('login_url', views.login_url_view, name='insurance-connectionless_url'),
    re_path(r'^topic/', views.webhook_catch_all_view, name='insurance-webhook-catchall')

]
