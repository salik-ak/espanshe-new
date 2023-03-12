from django.urls import path
from category import views


urlpatterns = [
    path('user-category/',views.user_category,name='user_category'),
]