from django.urls import path

from . import views

urlpatterns = [
    path("jobs/", views.list_processing_jobs, name="list-processing-jobs"),
    path("jobs/create/", views.create_processing_job, name="create-processing-job"),
]
