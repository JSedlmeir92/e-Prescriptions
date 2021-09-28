from django.urls import path
from . import views
from pharmacy.views import PrescriptionListView

urlpatterns = [
    path('', views.home_view, name='pharmacy-home'),
    path('login/', views.login_view, name='pharmacy-connection'),
    path('login/<int:way>', views.login_view, name='pharmacy-connection'),
    path('login-connectionless/', views.login_connectionless_view, name='pharmacy-connectionless'),
    ## Pharmarcy- Invitation for connectionless proof
    path('login_url', views.login_url_view, name='pharmacy-connectionless_url'),
    # Pharmacy - prescription check  
    path('login-result/', views.login_result_view, name='pharmacy-connection_result'),
    path('login-result/<int:id>', views.login_result_view, name='pharmacy-connection_result'),
    # Pharmacy - spent prescription presentation 
    path('logged-in/', views.logged_in_view, name='pharmacy-logged_in'),

    # Pharmarcy - Prescription Overview
    path("prescription/", views.prescription_table_view, name="pharmacy-prescription-table"),
    path('prescription/detail/<int:id>/', views.prescription_detail_view, name='pharmacy-prescription_detail'),
    path('prescription/delete_item/<int:id>', views.prescription_delete_item_view, name="pharmacy-prescription_delete_item"),
    path('prescription/check_item/<int:id>', views.prescription_check_item_view, name="pharmacy-prescription_check_item"),

    ## WEBHOOKS
    #
    path('topic/connections/', views.webhook_connection_view, name='pharmacy-webhook_connection'),
    #
    path('topic/present_proof/', views.webhook_proof_view, name='pharmacy-webhook_proof'),
]