from django.urls import path
from . import views
from .views import import_csv_data


urlpatterns = [
    path("visualization/", views.data_visualization, name="data_visualization"), 
    path("import/", views.import_csv_data, name="import_csv_data"),
]