
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

# importa las excepciones personalizadas
from .domain.exceptions import (
    CategoryValueError,
    CategoryValidationError,
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    CategoryOperationNotAllowedError,
    CategoryPermissionError
)

# importa las excepciones de repositorio
from .infrastructure.exceptions import (
    ConnectionDataBaseError,
    RepositoryError
)

# Importar formularios específicos de la entidad
from app.category_forms import (
    CategoryCreateForm, 
    CategoryEditGetForm, 
    CategoryEditPostForm, 
    CategoryViewForm
)

# Importar servicios específicos del dominio
from app.services.category_service import CategoryService

# Importar repositorios específicos de la infraestructura
from app.infrastructure.category_repository import CategoryRepository


def category_list(request):
    """
    Vista genérica para mostrar una lista de todas las instancias de category.
    """

    categoryList = [] #inicialize list

    categoryService = CategoryService(repository=CategoryRepository()) # Instanciar el servicio

    # Obtener la lista del repositorio
    try:
        categoryList = categoryService.list()

    except (CategoryValueError) as e:
        messages.error(request,  str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    # Renderizar la plantilla con la lista
    return render(request, 'app/category_web_list.html', {
        'categoryList': categoryList
    })


def category_create(request):
    """
    Vista genérica para crear una nueva instancia de category utilizando un servicio.
    """

    if request.method == "POST":

        # Validar los datos del formulario
        form = CategoryCreateForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            categoryService = CategoryService(repository=CategoryRepository()) # Instanciar el servicio

            # Obtener el ID de la entidad relacionada si existe
            external_id = request.POST.get('external_id', None)

            # Obtener la lista de ids de externals seleccionadas
            externals_ids = form_data.get('externals', [])

            try:
                # LLamar al servicio de creación
                categoryService.create(data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito y redirigir
                messages.success(request, f"Successfully created category")
                return redirect('app:category_list')

            except CategoryAlreadyExistsError as e:
                messages.error(request, "Already Exists Error: " + str(e))
            except (CategoryValueError, CategoryValidationError) as e:
                form.add_error(None, "Validation Error: " + str(e))
            except (ConnectionDataBaseError, RepositoryError) as e:
                messages.error(request, "There was an error accessing the database or repository: " + str(e))
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))
        else:
            messages.error(request, "There were errors in the form. Please correct them")
    else:
        # Formulario vacío para solicitudes GET
        form = CategoryCreateForm()

    # Renderizar la plantilla con el formulario
    return render(request, 'app/category_web_create.html', {'form': form}) 


def category_edit(request, id=None):
    """
    Vista genérica para editar una instancia existente de category utilizando un servicio.
    """

    if id is None:
        # Redireccion si no se proporciona un ID
        return redirect('app:category_list')

    categoryService = CategoryService(repository=CategoryRepository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        category = categoryService.retrieve(entity_id=id)

    except CategoryNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))
        return redirect('app:category_list')
    except CategoryValueError as e:
        messages.error(request,  "Value Error: " + str(e))
        return redirect('app:category_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app:category_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app:category_list')

    if request.method == "POST":

        # Validar los datos del formulario
        form = CategoryEditPostForm(request.POST)

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
                categoryService.update(entity_id=id, data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito
                messages.success(request, f"Successfully updated category")

                # Redireccionar a la lista de categorys
                return redirect('app:category_list')

            except CategoryNotFoundError as e:
                messages.error(request,  "Not Found Error: " + str(e))                
            except (CategoryValueError, CategoryValidationError) as e:
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
        form = CategoryEditGetForm(initial={
            'id': category['id'],            
            'attributeName': category['attributeName'],
            'attributeEmail': category['attributeEmail']
        })

    # Renderizar la plantilla con el formulario
    return render(request, 'app/category_web_edit.html', {'form': form})


def category_detail(request, id=None):
    """
    Vista genérica para mostrar los detalles de una instancia específica de category.
    """
    if id is None:
        return redirect('app:category_list')

    categoryService = CategoryService(repository=CategoryRepository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        category = categoryService.retrieve(entity_id=id)

    except CategoryNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))        
        return redirect('app:category_list')
    except CategoryValueError as e:
        messages.error(request,  str(e))
        return redirect('app:category_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app:category_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app:category_list')

    # Renderizar la plantilla con el formulario de vista
    form = CategoryViewForm(initial={
        'attributeName': category['attributeName'],
        'attributeEmail': category['attributeEmail']
    })

    return render(request, 'app/category_web_detail.html', {'form': form})


def category_delete(request, id=None):
    """
    Vista genérica para eliminar una instancia existente de category utilizando un servicio.
    """
    if id is None:
        messages.error(request, "Non Valid id to delete")
        return redirect('app:category_list')

    categoryService = CategoryService(repository=CategoryRepository()) # Instanciar el servicio

    try:
        # LLamar al servicio de eliminación
        categoryService.delete(entity_id=id)
        messages.success(request, f"Successfully deleted category")

    except CategoryNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))             
    except (CategoryValueError, CategoryValidationError) as e:
        messages.error(request,  "Validation Error: " + str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    return redirect('app:category_list')

