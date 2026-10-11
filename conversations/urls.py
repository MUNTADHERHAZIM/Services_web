from django.urls import path
from . import views

app_name = 'conversations'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('<int:conversation_id>/', views.chat_detail_view, name='chat_detail'),
    path('<int:conversation_id>/send/', views.send_message_view, name='send_message'),
    path('start/<int:recipient_id>/', views.start_conversation_view, name='start_conversation'),
]
