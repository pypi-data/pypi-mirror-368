
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

# importa las excepciones personalizadas
from .domain.exceptions import (
    ShorturlValueError,
    ShorturlValidationError,
    ShorturlAlreadyExistsError,
    ShorturlNotFoundError,
    ShorturlOperationNotAllowedError,
    ShorturlPermissionError
)

# importa las excepciones de repositorio
from .infrastructure.exceptions import (
    ConnectionDataBaseError,
    RepositoryError
)

# Importar formularios específicos de la entidad
from app.shorturl_forms import (
    ShorturlCreateForm, 
    ShorturlEditGetForm, 
    ShorturlEditPostForm, 
    ShorturlViewForm
)

# Importar servicios específicos del dominio
from app.services.shorturl_service import ShorturlService

# Importar repositorios específicos de la infraestructura
from app.infrastructure.shorturl_repository import ShorturlRepository


def shorturl_list(request):
    """
    Vista genérica para mostrar una lista de todas las instancias de shorturl.
    """

    shorturlList = [] #inicialize list

    shorturlService = ShorturlService(repository=ShorturlRepository()) # Instanciar el servicio

    # Obtener la lista del repositorio
    try:
        shorturlList = shorturlService.list()

    except (ShorturlValueError) as e:
        messages.error(request,  str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    # Renderizar la plantilla con la lista
    return render(request, 'app/shorturl_web_list.html', {
        'shorturlList': shorturlList
    })


def shorturl_create(request):
    """
    Vista genérica para crear una nueva instancia de shorturl utilizando un servicio.
    """

    if request.method == "POST":

        # Validar los datos del formulario
        form = ShorturlCreateForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            shorturlService = ShorturlService(repository=ShorturlRepository()) # Instanciar el servicio

            # Obtener el ID de la entidad relacionada si existe
            external_id = request.POST.get('external_id', None)

            # Obtener la lista de ids de externals seleccionadas
            externals_ids = form_data.get('externals', [])

            try:
                # LLamar al servicio de creación
                shorturlService.create(data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito y redirigir
                messages.success(request, f"Successfully created shorturl")
                return redirect('app:shorturl_list')

            except ShorturlAlreadyExistsError as e:
                messages.error(request, "Already Exists Error: " + str(e))
            except (ShorturlValueError, ShorturlValidationError) as e:
                form.add_error(None, "Validation Error: " + str(e))
            except (ConnectionDataBaseError, RepositoryError) as e:
                messages.error(request, "There was an error accessing the database or repository: " + str(e))
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))
        else:
            messages.error(request, "There were errors in the form. Please correct them")
    else:
        # Formulario vacío para solicitudes GET
        form = ShorturlCreateForm()

    # Renderizar la plantilla con el formulario
    return render(request, 'app/shorturl_web_create.html', {'form': form}) 


def shorturl_edit(request, id=None):
    """
    Vista genérica para editar una instancia existente de shorturl utilizando un servicio.
    """

    if id is None:
        # Redireccion si no se proporciona un ID
        return redirect('app:shorturl_list')

    shorturlService = ShorturlService(repository=ShorturlRepository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        shorturl = shorturlService.retrieve(entity_id=id)

    except ShorturlNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))
        return redirect('app:shorturl_list')
    except ShorturlValueError as e:
        messages.error(request,  "Value Error: " + str(e))
        return redirect('app:shorturl_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app:shorturl_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app:shorturl_list')

    if request.method == "POST":

        # Validar los datos del formulario
        form = ShorturlEditPostForm(request.POST)

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
                shorturlService.update(entity_id=id, data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito
                messages.success(request, f"Successfully updated shorturl")

                # Redireccionar a la lista de shorturls
                return redirect('app:shorturl_list')

            except ShorturlNotFoundError as e:
                messages.error(request,  "Not Found Error: " + str(e))                
            except (ShorturlValueError, ShorturlValidationError) as e:
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
        form = ShorturlEditGetForm(initial={
            'id': shorturl['id'],            
            'attributeName': shorturl['attributeName'],
            'attributeEmail': shorturl['attributeEmail']
        })

    # Renderizar la plantilla con el formulario
    return render(request, 'app/shorturl_web_edit.html', {'form': form})


def shorturl_detail(request, id=None):
    """
    Vista genérica para mostrar los detalles de una instancia específica de shorturl.
    """
    if id is None:
        return redirect('app:shorturl_list')

    shorturlService = ShorturlService(repository=ShorturlRepository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        shorturl = shorturlService.retrieve(entity_id=id)

    except ShorturlNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))        
        return redirect('app:shorturl_list')
    except ShorturlValueError as e:
        messages.error(request,  str(e))
        return redirect('app:shorturl_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app:shorturl_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app:shorturl_list')

    # Renderizar la plantilla con el formulario de vista
    form = ShorturlViewForm(initial={
        'attributeName': shorturl['attributeName'],
        'attributeEmail': shorturl['attributeEmail']
    })

    return render(request, 'app/shorturl_web_detail.html', {'form': form})


def shorturl_delete(request, id=None):
    """
    Vista genérica para eliminar una instancia existente de shorturl utilizando un servicio.
    """
    if id is None:
        messages.error(request, "Non Valid id to delete")
        return redirect('app:shorturl_list')

    shorturlService = ShorturlService(repository=ShorturlRepository()) # Instanciar el servicio

    try:
        # LLamar al servicio de eliminación
        shorturlService.delete(entity_id=id)
        messages.success(request, f"Successfully deleted shorturl")

    except ShorturlNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))             
    except (ShorturlValueError, ShorturlValidationError) as e:
        messages.error(request,  "Validation Error: " + str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    return redirect('app:shorturl_list')

