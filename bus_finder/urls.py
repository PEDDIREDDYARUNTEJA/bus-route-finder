from django.urls import path
from . import views

app_name = 'bus_finder'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/stops/', views.api_stops, name='api_stops'),
    path('api/search/', views.api_search, name='api_search'),
    
    # Custom Admin Login & Logout Routes
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # Custom Admin Dashboard Portal Routes (Protected)
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/bus/add/', views.bus_add, name='bus_add'),
    path('dashboard/bus/<int:bus_id>/edit/', views.bus_edit, name='bus_edit'),
    path('dashboard/bus/<int:bus_id>/delete/', views.bus_delete, name='bus_delete'),
    path('dashboard/stops/', views.stop_manage, name='stop_manage'),
    path('dashboard/stops/<int:stop_id>/delete/', views.stop_delete, name='stop_delete'),
]
