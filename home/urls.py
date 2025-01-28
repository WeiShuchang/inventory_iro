from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.landing_page_view, name="landing_url"),
    path('login/', views.user_login, name='login_url'),
    path('item-types/', views.item_types_list, name='item_types_list'),
    path('item-type/<int:pk>/', views.item_type_detail, name='item_type_detail'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
]
