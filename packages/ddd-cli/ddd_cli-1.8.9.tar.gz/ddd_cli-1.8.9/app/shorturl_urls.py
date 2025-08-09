
from django.urls import path

from . import shorturl_views

app_name = "app"

urlpatterns = [

    path('', shorturl_views.shorturl_list, name="index"),  # ← Esta es la URL por defecto    
    path('shorturl-list/', shorturl_views.shorturl_list, name="shorturl_list"),
    path('shorturl-create/', shorturl_views.shorturl_create, name="shorturl_create"),
    path('shorturl-edit/<int:id>', shorturl_views.shorturl_edit, name="shorturl_edit"),
    path('shorturl-detail/<int:id>', shorturl_views.shorturl_detail, name="shorturl_detail"),
    path('shorturl-delete/<int:id>', shorturl_views.shorturl_delete, name="shorturl_delete"),    

]
