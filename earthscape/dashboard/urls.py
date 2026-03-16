from django.urls import path

from . import views

urlpatterns = [
    path("summary/", views.dashboard_summary, name="dashboard-summary"),
    path("preferences/", views.update_preferences, name="update-preferences"),
    path("alerts/rules/create/", views.create_alert_rule, name="create-alert-rule"),
    path("alerts/rules/<int:rule_id>/events/create/", views.raise_alert_event, name="raise-alert-event"),
    path("support/tickets/create/", views.create_support_ticket, name="create-support-ticket"),
]
