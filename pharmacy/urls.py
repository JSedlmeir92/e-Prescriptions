from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='pharmacy-home'),

    path('login/', views.login_view, name='pharmacy-connection'),

    path('logging-in/', views.login_loading_view, name='pharmacy-connection_loading'),

    path('login-result/', views.login_result_view, name='pharmacy-connection_result'),

    path('logged-in/', views.logged_in_view, name='pharmacy-logged_in'),
    # webhooks
    path('topic/connections/', views.webhook_connection_view, name='pharmacy-webhook_connection'),
    
    path('topic/present_proof/', views.webhook_proof_view, name='pharmacy-webhook_proof'),
]