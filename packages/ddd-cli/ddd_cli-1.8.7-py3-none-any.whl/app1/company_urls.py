
from django.urls import path

from . import company_views

app_name = "app1"

urlpatterns = [

    path('', company_views.company_list, name="index"),  # ← Esta es la URL por defecto    
    path('company-list/', company_views.company_list, name="company_list"),
    path('company-create/', company_views.company_create, name="company_create"),
    path('company-edit/<int:id>', company_views.company_edit, name="company_edit"),
    path('company-detail/<int:id>', company_views.company_detail, name="company_detail"),
    path('company-delete/<int:id>', company_views.company_delete, name="company_delete"),    

]
