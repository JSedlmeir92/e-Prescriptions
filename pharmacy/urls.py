from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='work-home'),
    path('login/', views.login_view, name='work-login'),
    path('logging-in/', views.login_loading_view, name='work-login_loading'),
    path('login-result/', views.login_result_view, name='work-login_result'),
    path('logged-in/', views.logged_in_view, name='work-logged_in'),
    # webhooks
    path('topic/connections/', views.webhook_connection_view, name='work-webhook_connection'),
    path('topic/present_proof/', views.webhook_proof_view, name='work-webhook_proof'),
]