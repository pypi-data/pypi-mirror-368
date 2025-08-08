
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

# importa las excepciones personalizadas
from .domain.exceptions import (
    CompanyValueError,
    CompanyValidationError,
    CompanyAlreadyExistsError,
    CompanyNotFoundError,
    CompanyOperationNotAllowedError,
    CompanyPermissionError
)

# importa las excepciones de repositorio
from .infrastructure.exceptions import (
    ConnectionDataBaseError,
    RepositoryError
)

# Importar formularios específicos de la entidad
from app1.company_forms import (
    CompanyCreateForm, 
    CompanyEditGetForm, 
    CompanyEditPostForm, 
    CompanyViewForm
)

# Importar servicios específicos del dominio
from app1.services.company_service import CompanyService

# Importar repositorios específicos de la infraestructura
from app1.infrastructure.company_repository import CompanyRepository


def company_list(request):
    """
    Vista genérica para mostrar una lista de todas las instancias de company.
    """

    companyList = [] #inicialize list

    companyService = CompanyService(repository=CompanyRepository()) # Instanciar el servicio

    # Obtener la lista del repositorio
    try:
        companyList = companyService.list()

    except (CompanyValueError) as e:
        messages.error(request,  str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    # Renderizar la plantilla con la lista
    return render(request, 'app1/company_web_list.html', {
        'companyList': companyList
    })


def company_create(request):
    """
    Vista genérica para crear una nueva instancia de company utilizando un servicio.
    """

    if request.method == "POST":

        # Validar los datos del formulario
        form = CompanyCreateForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            companyService = CompanyService(repository=CompanyRepository()) # Instanciar el servicio

            # Obtener el ID de la entidad relacionada si existe
            external_id = request.POST.get('external_id', None)

            # Obtener la lista de ids de externals seleccionadas
            externals_ids = form_data.get('externals', [])

            try:
                # LLamar al servicio de creación
                companyService.create(data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito y redirigir
                messages.success(request, f"Successfully created company")
                return redirect('app1:company_list')

            except CompanyAlreadyExistsError as e:
                messages.error(request, "Already Exists Error: " + str(e))
            except (CompanyValueError, CompanyValidationError) as e:
                form.add_error(None, "Validation Error: " + str(e))
            except (ConnectionDataBaseError, RepositoryError) as e:
                messages.error(request, "There was an error accessing the database or repository: " + str(e))
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))
        else:
            messages.error(request, "There were errors in the form. Please correct them")
    else:
        # Formulario vacío para solicitudes GET
        form = CompanyCreateForm()

    # Renderizar la plantilla con el formulario
    return render(request, 'app1/company_web_create.html', {'form': form}) 


def company_edit(request, id=None):
    """
    Vista genérica para editar una instancia existente de company utilizando un servicio.
    """

    if id is None:
        # Redireccion si no se proporciona un ID
        return redirect('app1:company_list')

    companyService = CompanyService(repository=CompanyRepository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        company = companyService.retrieve(entity_id=id)

    except CompanyNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))
        return redirect('app1:company_list')
    except CompanyValueError as e:
        messages.error(request,  "Value Error: " + str(e))
        return redirect('app1:company_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app1:company_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app1:company_list')

    if request.method == "POST":

        # Validar los datos del formulario
        form = CompanyEditPostForm(request.POST)

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
                companyService.update(entity_id=id, data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito
                messages.success(request, f"Successfully updated company")

                # Redireccionar a la lista de companys
                return redirect('app1:company_list')

            except CompanyNotFoundError as e:
                messages.error(request,  "Not Found Error: " + str(e))                
            except (CompanyValueError, CompanyValidationError) as e:
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
        form = CompanyEditGetForm(initial={
            'id': company['id'],            
            'attributeName': company['attributeName'],
            'attributeEmail': company['attributeEmail']
        })

    # Renderizar la plantilla con el formulario
    return render(request, 'app1/company_web_edit.html', {'form': form})


def company_detail(request, id=None):
    """
    Vista genérica para mostrar los detalles de una instancia específica de company.
    """
    if id is None:
        return redirect('app1:company_list')

    companyService = CompanyService(repository=CompanyRepository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        company = companyService.retrieve(entity_id=id)

    except CompanyNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))        
        return redirect('app1:company_list')
    except CompanyValueError as e:
        messages.error(request,  str(e))
        return redirect('app1:company_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app1:company_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app1:company_list')

    # Renderizar la plantilla con el formulario de vista
    form = CompanyViewForm(initial={
        'attributeName': company['attributeName'],
        'attributeEmail': company['attributeEmail']
    })

    return render(request, 'app1/company_web_detail.html', {'form': form})


def company_delete(request, id=None):
    """
    Vista genérica para eliminar una instancia existente de company utilizando un servicio.
    """
    if id is None:
        messages.error(request, "Non Valid id to delete")
        return redirect('app1:company_list')

    companyService = CompanyService(repository=CompanyRepository()) # Instanciar el servicio

    try:
        # LLamar al servicio de eliminación
        companyService.delete(entity_id=id)
        messages.success(request, f"Successfully deleted company")

    except CompanyNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))             
    except (CompanyValueError, CompanyValidationError) as e:
        messages.error(request,  "Validation Error: " + str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    return redirect('app1:company_list')

