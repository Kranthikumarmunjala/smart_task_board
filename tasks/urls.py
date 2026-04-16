from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_task),
    path('list/', views.list_tasks),
    path('complete/', views.complete_task),
]