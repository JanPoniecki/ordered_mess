from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('container-browser/', views.container_browser, name='container_browser'),
    path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    path('upload/', views.upload_image, name='upload_image'),
    path('room-browser/', views.room_browser, name='room_browser'),
]