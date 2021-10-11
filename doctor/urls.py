from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='doctor-home'),
    # Doctor - Schema
    path('schema/', views.schema_view, name='doctor-schema'),
    # Doctor - Credential definition
    path('cred_def/', views.cred_def_view, name='doctor-cred_def'),
    # Doctor - Revocation registry
    path('rev_reg/', views.rev_reg_view, name='doctor-rev_reg'),
    # Doctor - Connection
    path('connection/', views.connection_view, name='doctor-connection'),
    # Doctor - Issue prescription
    path('issue_cred/', views.issue_cred_view, name='doctor-issue_cred'),
    # Doctor - Revoke prescription
    path('revoke_cred/', views.revoke_cred_view, name='doctor-revoke_cred'),
    # Doctor - Detailed overview of a specific prescription
    path('cred_detail/<int:id>/', views.cred_detail_view, name='doctor-cred_detail')
]