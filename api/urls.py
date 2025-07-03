from django.urls import path
from api.views import chave_views, provas_views, user_views, student_views

urlpatterns = [
    path('api/register/', user_views.register, name='register'),
    path('api/login/', user_views.login, name='login'),
    path('api/get-me/', user_views.get_me, name='get_me'),
    path('api/upload-test/', provas_views.upload_images, name='upload_test_images'),
    path('api/update-student/<int:student_id>/', student_views.update_student, name='update_student')
]