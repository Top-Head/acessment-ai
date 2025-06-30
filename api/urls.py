from django.urls import path
from views import chave_views, provas_views, user_views

urlspatterns = [
    path('api/register/', user_views.register, name='register'),
    path('api/login/', user_views.login, name='login'),
    path('api/get-me/', user_views.get_me, name='get_me'),
]