from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

# importa las excepciones personalizadas
from .domain.exceptions import (
    [[ entity_name.capitalize() ]]ValueError,
    [[ entity_name.capitalize() ]]ValidationError,
    [[ entity_name.capitalize() ]]AlreadyExistsError,
    [[ entity_name.capitalize() ]]NotFoundError,
    [[ entity_name.capitalize() ]]OperationNotAllowedError,
    [[ entity_name.capitalize() ]]PermissionError
)

# importa las excepciones de repositorio
from .infrastructure.exceptions import (
    ConnectionDataBaseError,
    RepositoryError
)

# Importar formularios específicos de la entidad
from [[ app_name.lower() ]].[[ entity_name.lower() ]]_forms import (
    [[ entity_name.capitalize() ]]CreateForm, 
    [[ entity_name.capitalize() ]]EditGetForm, 
    [[ entity_name.capitalize() ]]EditPostForm, 
    [[ entity_name.capitalize() ]]ViewForm
)

# Importar servicios específicos del dominio
from [[ app_name.lower() ]].services.[[ entity_name.lower() ]]_service import [[ entity_name.capitalize() ]]Service

# Importar repositorios específicos de la infraestructura
from [[ app_name.lower() ]].infrastructure.[[ entity_name.lower() ]]_repository import [[ entity_name.capitalize() ]]Repository


def [[ entity_name.lower() ]]_list(request):
    """
    Vista genérica para mostrar una lista de todas las instancias de [[ entity_name.lower() ]].
    """

    [[ entity_name.lower() ]]List = [] #inicialize list

    [[ entity_name.lower() ]]Service = [[ entity_name.capitalize() ]]Service(repository=[[ entity_name.capitalize() ]]Repository()) # Instanciar el servicio

    # Obtener la lista del repositorio
    try:
        [[ entity_name.lower() ]]List = [[ entity_name.lower() ]]Service.list()

    except ([[ entity_name.capitalize() ]]ValueError) as e:
        messages.error(request,  str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    # Renderizar la plantilla con la lista
    return render(request, '[[ relative_app_path.lower() ]]/[[ entity_name.lower() ]]_web_list.html', {
        '[[ entity_name.lower() ]]List': [[ entity_name.lower() ]]List
    })


def [[ entity_name.lower() ]]_create(request):
    """
    Vista genérica para crear una nueva instancia de [[ entity_name.lower() ]] utilizando un servicio.
    """

    if request.method == "POST":

        # Validar los datos del formulario
        form = [[ entity_name.capitalize() ]]CreateForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            [[ entity_name.lower() ]]Service = [[ entity_name.capitalize() ]]Service(repository=[[ entity_name.capitalize() ]]Repository()) # Instanciar el servicio

            # Obtener el ID de la entidad relacionada si existe
            external_id = request.POST.get('external_id', None)

            # Obtener la lista de ids de externals seleccionadas
            externals_ids = form_data.get('externals', [])

            try:
                # LLamar al servicio de creación
                [[ entity_name.lower() ]]Service.create(data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito y redirigir
                messages.success(request, f"Successfully created [[ entity_name.lower() ]]")
                return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

            except [[ entity_name.capitalize() ]]AlreadyExistsError as e:
                messages.error(request, "Already Exists Error: " + str(e))
            except ([[ entity_name.capitalize() ]]ValueError, [[ entity_name.capitalize() ]]ValidationError) as e:
                form.add_error(None, "Validation Error: " + str(e))
            except (ConnectionDataBaseError, RepositoryError) as e:
                messages.error(request, "There was an error accessing the database or repository: " + str(e))
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))
        else:
            messages.error(request, "There were errors in the form. Please correct them")
    else:
        # Formulario vacío para solicitudes GET
        form = [[ entity_name.capitalize() ]]CreateForm()

    # Renderizar la plantilla con el formulario
    return render(request, '[[ relative_app_path.lower() ]]/[[ entity_name.lower() ]]_web_create.html', {'form': form}) 


def [[ entity_name.lower() ]]_edit(request, id=None):
    """
    Vista genérica para editar una instancia existente de [[ entity_name.lower() ]] utilizando un servicio.
    """

    if id is None:
        # Redireccion si no se proporciona un ID
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

    [[ entity_name.lower() ]]Service = [[ entity_name.capitalize() ]]Service(repository=[[ entity_name.capitalize() ]]Repository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        [[ entity_name.lower() ]] = [[ entity_name.lower() ]]Service.retrieve(entity_id=id)

    except [[ entity_name.capitalize() ]]NotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')
    except [[ entity_name.capitalize() ]]ValueError as e:
        messages.error(request,  "Value Error: " + str(e))
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

    if request.method == "POST":

        # Validar los datos del formulario
        form = [[ entity_name.capitalize() ]]EditPostForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data

            try:
                # obtenemos del request los campos especiales del formulario
                # ejemplo: password = request.POST.get('password', None)
                # ejemplo: photo = request.FILES.get('photo', None)
                # y los enviamos como parametros al servicio de actualizacion

                # Obtener el ID de la entidad relacionada si existe
                external_id = request.POST.get('external_id', None)

                # Obtener la lista de ids de externals seleccionadas
                externals_ids = form_data.get('externals', [])                

                # LLamar al servicio de actualización
                [[ entity_name.lower() ]]Service.update(entity_id=id, data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito
                messages.success(request, f"Successfully updated [[ entity_name.lower() ]]")

                # Redireccionar a la lista de [[ entity_name.lower() ]]s
                return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

            except [[ entity_name.capitalize() ]]NotFoundError as e:
                messages.error(request,  "Not Found Error: " + str(e))                
            except ([[ entity_name.capitalize() ]]ValueError, [[ entity_name.capitalize() ]]ValidationError) as e:
                form.add_error(None, "Validation Error: " + str(e))
            except (ConnectionDataBaseError, RepositoryError) as e:
                messages.error(request, "There was an error accessing the database or repository: " + str(e))
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))

        else:
            messages.error(request, "There were errors in the form. Please correct them")

    # request.method == "GET":
    else:  
        # Initialize the form with existing data
        form = [[ entity_name.capitalize() ]]EditGetForm(initial={
            'id': [[ entity_name.lower() ]]['id'],            
            'attributeName': [[ entity_name.lower() ]]['attributeName'],
            'attributeEmail': [[ entity_name.lower() ]]['attributeEmail']
        })

    # Renderizar la plantilla con el formulario
    return render(request, '[[ relative_app_path.lower() ]]/[[ entity_name.lower() ]]_web_edit.html', {'form': form})


def [[ entity_name.lower() ]]_detail(request, id=None):
    """
    Vista genérica para mostrar los detalles de una instancia específica de [[ entity_name.lower() ]].
    """
    if id is None:
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

    [[ entity_name.lower() ]]Service = [[ entity_name.capitalize() ]]Service(repository=[[ entity_name.capitalize() ]]Repository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        [[ entity_name.lower() ]] = [[ entity_name.lower() ]]Service.retrieve(entity_id=id)

    except [[ entity_name.capitalize() ]]NotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))        
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')
    except [[ entity_name.capitalize() ]]ValueError as e:
        messages.error(request,  str(e))
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

    # Renderizar la plantilla con el formulario de vista
    form = [[ entity_name.capitalize() ]]ViewForm(initial={
        'attributeName': [[ entity_name.lower() ]]['attributeName'],
        'attributeEmail': [[ entity_name.lower() ]]['attributeEmail']
    })

    return render(request, '[[ relative_app_path.lower() ]]/[[ entity_name.lower() ]]_web_detail.html', {'form': form})


def [[ entity_name.lower() ]]_delete(request, id=None):
    """
    Vista genérica para eliminar una instancia existente de [[ entity_name.lower() ]] utilizando un servicio.
    """
    if id is None:
        messages.error(request, "Non Valid id to delete")
        return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

    [[ entity_name.lower() ]]Service = [[ entity_name.capitalize() ]]Service(repository=[[ entity_name.capitalize() ]]Repository()) # Instanciar el servicio

    try:
        # LLamar al servicio de eliminación
        [[ entity_name.lower() ]]Service.delete(entity_id=id)
        messages.success(request, f"Successfully deleted [[ entity_name.lower() ]]")

    except [[ entity_name.capitalize() ]]NotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))             
    except ([[ entity_name.capitalize() ]]ValueError, [[ entity_name.capitalize() ]]ValidationError) as e:
        messages.error(request,  "Validation Error: " + str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    return redirect('[[ app_route.lower() ]]:[[ entity_name.lower() ]]_list')

