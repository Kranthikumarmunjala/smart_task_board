# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import TaskViewSet

# router = DefaultRouter()
# router.register(r'tasks', TaskViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
# ]
from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_task),
    path('list/', views.list_tasks),
    path('complete/', views.complete_task),
]