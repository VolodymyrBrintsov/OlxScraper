from django.urls import path
from .views import home, extract, all_adds

urlpatterns = [
    path('', home, name='home'),
    path('extract/', extract, name='extract'),
    path('all_adds/', all_adds, name='all_adds'),
]