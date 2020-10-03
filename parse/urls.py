from django.urls import path
from .views import home, extract, all_adds, download, login_user, logout_user

urlpatterns = [
    path('', home, name='home'),
    path('extract/', extract, name='extract'),
    path('all_adds/', all_adds, name='all_adds'),
    path('download/', download, name='download'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
]