from django.urls import path

from . import views

urlpatterns = [
    path("sources/", views.list_data_sources, name="list-data-sources"),
    path("datasets/", views.list_datasets, name="list-datasets"),
    path("datasets/create/", views.create_dataset, name="create-dataset"),
    path("sources/<int:source_id>/trigger/", views.trigger_ingestion_run, name="trigger-ingestion-run"),
]
