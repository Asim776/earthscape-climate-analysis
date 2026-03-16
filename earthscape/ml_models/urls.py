from django.urls import path

from . import views

urlpatterns = [
    path("models/", views.list_models, name="list-models"),
    path("models/register/", views.register_model, name="register-model"),
    path("predictions/create/", views.create_prediction, name="create-prediction"),
]
