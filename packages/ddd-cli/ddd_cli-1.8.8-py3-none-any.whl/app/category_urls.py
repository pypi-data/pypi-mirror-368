
from django.urls import path

from . import category_views

app_name = "app"

urlpatterns = [

    path('', category_views.category_list, name="index"),  # ← Esta es la URL por defecto    
    path('category-list/', category_views.category_list, name="category_list"),
    path('category-create/', category_views.category_create, name="category_create"),
    path('category-edit/<int:id>', category_views.category_edit, name="category_edit"),
    path('category-detail/<int:id>', category_views.category_detail, name="category_detail"),
    path('category-delete/<int:id>', category_views.category_delete, name="category_delete"),    

]
