
# domain/exceptions.py

class CategoryError(Exception):
    """Excepción base para errores relacionados con el dominio Category."""
    pass


class CategoryValueError(CategoryError):
    """Error de valor en atributos de la entidad Category."""
    def __init__(self, detail: str, field: str = "value"):
        self.field = field
        self.detail = detail
        if field == "value":
            super().__init__(f"Error de valor: {detail}")
        else:
            super().__init__(f"Error en el campo '{field}': {detail}")


class CategoryValidationError(CategoryError):
    """Errores de validación de datos antes de guardar el modelo."""
    def __init__(self, errors):
        self.errors = errors
        super().__init__("La validación de la Category falló.")


class CategoryAlreadyExistsError(CategoryError):
    """Cuando se intenta crear una Category que ya existe."""
    def __init__(self, cause):
        self.cause = cause
        super().__init__(f"Category existe.")


class CategoryNotFoundError(CategoryError):
    """Cuando se intenta acceder a una Category inexistente."""
    def __init__(self, id):
        self.id = id
        super().__init__(f"Category con ID {id} no encontrada.")


class CategoryOperationNotAllowedError(CategoryError):
    """Cuando se intenta realizar una operación no permitida."""
    def __init__(self, operation_name: str):
        super().__init__(f"La operación '{operation_name}' no está permitida en esta Category.")        


class CategoryPermissionError(CategoryError):
    """Cuando el usuario no tiene permisos para modificar o acceder."""
    def __init__(self):
        super().__init__("No tienes permisos para realizar esta acción sobre la Category.")      
