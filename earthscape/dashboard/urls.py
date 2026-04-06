from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('analysis/', views.analysis_view, name='analysis'),
    path('charts/', views.charts_view, name='charts'),
    path('predictions/', views.predictions_view, name='predictions'),
]