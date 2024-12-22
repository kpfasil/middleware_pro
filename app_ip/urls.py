from django.urls import path
from . import views
urlpatterns = [
    path('ip_block/', views.ip_block,name="ip_block"),
]
