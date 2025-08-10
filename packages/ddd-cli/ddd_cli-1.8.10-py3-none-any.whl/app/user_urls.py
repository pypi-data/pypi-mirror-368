
from django.urls import path

from . import user_views

app_name = "app"

urlpatterns = [

    path('', user_views.user_list, name="index"),  # ← Esta es la URL por defecto    
    path('user-list/', user_views.user_list, name="user_list"),
    path('user-create/', user_views.user_create, name="user_create"),
    path('user-edit/<int:id>', user_views.user_edit, name="user_edit"),
    path('user-detail/<int:id>', user_views.user_detail, name="user_detail"),
    path('user-delete/<int:id>', user_views.user_delete, name="user_delete"),    

]
