from django.urls import path

from . import [[ entity_name.lower() ]]_views

app_name = "[[ last_app_name.lower() ]]"

urlpatterns = [

    path('', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_list, name="index"),  # ← Esta es la URL por defecto    
    path('[[ entity_name.lower() ]]-list/', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_list, name="[[ entity_name.lower() ]]_list"),
    path('[[ entity_name.lower() ]]-create/', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_create, name="[[ entity_name.lower() ]]_create"),
    path('[[ entity_name.lower() ]]-edit/<int:id>', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_edit, name="[[ entity_name.lower() ]]_edit"),
    path('[[ entity_name.lower() ]]-detail/<int:id>', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_detail, name="[[ entity_name.lower() ]]_detail"),
    path('[[ entity_name.lower() ]]-delete/<int:id>', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_delete, name="[[ entity_name.lower() ]]_delete"),    

]
