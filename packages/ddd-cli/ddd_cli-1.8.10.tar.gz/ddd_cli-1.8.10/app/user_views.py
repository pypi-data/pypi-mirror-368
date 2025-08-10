
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

# importa las excepciones personalizadas
from .domain.exceptions import (
    UserValueError,
    UserValidationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserOperationNotAllowedError,
    UserPermissionError
)

# importa las excepciones de repositorio
from .infrastructure.exceptions import (
    ConnectionDataBaseError,
    RepositoryError
)

# Importar formularios específicos de la entidad
from app.user_forms import (
    UserCreateForm, 
    UserEditGetForm, 
    UserEditPostForm, 
    UserViewForm
)

# Importar servicios específicos del dominio
from app.services.user_service import UserService

# Importar repositorios específicos de la infraestructura
from app.infrastructure.user_repository import UserRepository


def user_list(request):
    """
    Vista genérica para mostrar una lista de todas las instancias de user.
    """

    userList = [] #inicialize list

    userService = UserService(repository=UserRepository()) # Instanciar el servicio

    # Obtener la lista del repositorio
    try:
        userList = userService.list()

    except (UserValueError) as e:
        messages.error(request,  str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    # Renderizar la plantilla con la lista
    return render(request, 'app/user_web_list.html', {
        'userList': userList
    })


def user_create(request):
    """
    Vista genérica para crear una nueva instancia de user utilizando un servicio.
    """

    if request.method == "POST":

        # Validar los datos del formulario
        form = UserCreateForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            userService = UserService(repository=UserRepository()) # Instanciar el servicio

            # Obtener el ID de la entidad relacionada si existe
            external_id = request.POST.get('external_id', None)

            # Obtener la lista de ids de externals seleccionadas
            externals_ids = form_data.get('externals', [])

            try:
                # LLamar al servicio de creación
                userService.create(data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito y redirigir
                messages.success(request, f"Successfully created user")
                return redirect('app:user_list')

            except UserAlreadyExistsError as e:
                messages.error(request, "Already Exists Error: " + str(e))
            except (UserValueError, UserValidationError) as e:
                form.add_error(None, "Validation Error: " + str(e))
            except (ConnectionDataBaseError, RepositoryError) as e:
                messages.error(request, "There was an error accessing the database or repository: " + str(e))
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))
        else:
            messages.error(request, "There were errors in the form. Please correct them")
    else:
        # Formulario vacío para solicitudes GET
        form = UserCreateForm()

    # Renderizar la plantilla con el formulario
    return render(request, 'app/user_web_create.html', {'form': form}) 


def user_edit(request, id=None):
    """
    Vista genérica para editar una instancia existente de user utilizando un servicio.
    """

    if id is None:
        # Redireccion si no se proporciona un ID
        return redirect('app:user_list')

    userService = UserService(repository=UserRepository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        user = userService.retrieve(entity_id=id)

    except UserNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))
        return redirect('app:user_list')
    except UserValueError as e:
        messages.error(request,  "Value Error: " + str(e))
        return redirect('app:user_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app:user_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app:user_list')

    if request.method == "POST":

        # Validar los datos del formulario
        form = UserEditPostForm(request.POST)

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
                userService.update(entity_id=id, data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito
                messages.success(request, f"Successfully updated user")

                # Redireccionar a la lista de users
                return redirect('app:user_list')

            except UserNotFoundError as e:
                messages.error(request,  "Not Found Error: " + str(e))                
            except (UserValueError, UserValidationError) as e:
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
        form = UserEditGetForm(initial={
            'id': user['id'],            
            'attributeName': user['attributeName'],
            'attributeEmail': user['attributeEmail']
        })

    # Renderizar la plantilla con el formulario
    return render(request, 'app/user_web_edit.html', {'form': form})


def user_detail(request, id=None):
    """
    Vista genérica para mostrar los detalles de una instancia específica de user.
    """
    if id is None:
        return redirect('app:user_list')

    userService = UserService(repository=UserRepository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        user = userService.retrieve(entity_id=id)

    except UserNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))        
        return redirect('app:user_list')
    except UserValueError as e:
        messages.error(request,  str(e))
        return redirect('app:user_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app:user_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app:user_list')

    # Renderizar la plantilla con el formulario de vista
    form = UserViewForm(initial={
        'attributeName': user['attributeName'],
        'attributeEmail': user['attributeEmail']
    })

    return render(request, 'app/user_web_detail.html', {'form': form})


def user_delete(request, id=None):
    """
    Vista genérica para eliminar una instancia existente de user utilizando un servicio.
    """
    if id is None:
        messages.error(request, "Non Valid id to delete")
        return redirect('app:user_list')

    userService = UserService(repository=UserRepository()) # Instanciar el servicio

    try:
        # LLamar al servicio de eliminación
        userService.delete(entity_id=id)
        messages.success(request, f"Successfully deleted user")

    except UserNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))             
    except (UserValueError, UserValidationError) as e:
        messages.error(request,  "Validation Error: " + str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    return redirect('app:user_list')

