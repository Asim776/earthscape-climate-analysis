from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('analysis/', views.analysis_view, name='analysis'),
    path('charts/', views.charts_view, name='charts'),
    path('predictions/', views.predictions_view, name='predictions'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]