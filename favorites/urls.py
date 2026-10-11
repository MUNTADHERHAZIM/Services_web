from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('', views.MyFavoritesView.as_view(), name='my_favorites'),
    path('toggle/<int:service_id>/', views.toggle_favorite, name='toggle_favorite'),
]
