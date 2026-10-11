from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.my_wallet_view, name='my_wallet'),
    path('deposit/', views.create_deposit_request_view, name='deposit'),
    path('withdraw/', views.create_withdrawal_request_view, name='withdraw'),
    path('deposit-request/<int:pk>/cancel/', views.cancel_deposit_request_view, name='cancel_deposit'),
    path('withdrawal-request/<int:pk>/cancel/', views.cancel_withdrawal_request_view, name='cancel_withdrawal'),
    path('api/deposit-method/<int:pk>/', views.deposit_method_info_api, name='deposit_method_api'),
    
    # وصولات وفواتير النظام الرسمية
    path('receipts/', views.my_receipts_view, name='my_receipts'),
    path('receipt/<str:receipt_number>/', views.receipt_detail_view, name='receipt_detail'),
    path('receipt/verify/<uuid:token>/', views.receipt_verify_view, name='receipt_verify'),
    path('receipt/order/<int:pk>/', views.request_receipt_view, name='request_receipt'),
    path('receipt/deposit/<int:pk>/', views.deposit_receipt_view, name='deposit_receipt'),
    path('receipt/withdrawal/<int:pk>/', views.withdrawal_receipt_view, name='withdrawal_receipt'),
    path('receipt/transaction/<int:pk>/', views.transaction_receipt_view, name='transaction_receipt'),
]
