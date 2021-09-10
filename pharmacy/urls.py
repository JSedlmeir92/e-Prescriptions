from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='pharmacy-home'),
    # Phamarcy - Invitation Creation
    path('login/', views.login_view, name='pharmacy-connection'),
    ## Pharmarcy- Invitation for connectionless proof
    # Pharmacy - Proof Request Recration --> auskommentiert
    # path('logging-in/', views.login_loading_view, name='pharmacy-connection_loading'),
    # Pharmarcy - Connectionless presentation-functionality
    path('login_url', views.login_url_view, name='pharmacy-connectionless_url'),
    path('login_link', views.login_link_view, name='pharmacy-connectionless_link'),

    # Pharmacy - prescription check  
    path('login-result/', views.login_result_view, name='pharmacy-connection_result'),
    # Pharmacy - spent prescription presentation 
    path('logged-in/', views.logged_in_view, name='pharmacy-logged_in'),
    ## WEBHOOKS
    #
    path('topic/connections/', views.webhook_connection_view, name='pharmacy-webhook_connection'),
    #
    path('topic/present_proof/', views.webhook_proof_view, name='pharmacy-webhook_proof'),
]