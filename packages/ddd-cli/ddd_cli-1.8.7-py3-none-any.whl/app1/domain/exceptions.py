
# domain/exceptions.py

class CompanyError(Exception):
    """Excepción base para errores relacionados con el dominio Company."""
    pass


class CompanyValueError(CompanyError):
    """Error de valor en atributos de la entidad Company."""
    def __init__(self, field: str, detail: str):
        self.field = field
        self.detail = detail
        super().__init__(f"Error en el campo '{field}': {detail}")


class CompanyValidationError(CompanyError):
    """Errores de validación de datos antes de guardar el modelo."""
    def __init__(self, errors):
        self.errors = errors
        super().__init__("La validación de la Company falló.")


class CompanyAlreadyExistsError(CompanyError):
    """Cuando se intenta crear una Company que ya existe."""
    def __init__(self, cause):
        self.cause = cause
        super().__init__(f"Company existe.")


class CompanyNotFoundError(CompanyError):
    """Cuando se intenta acceder a una Company inexistente."""
    def __init__(self, id):
        self.id = id
        super().__init__(f"Company con ID {id} no encontrada.")


class CompanyOperationNotAllowedError(CompanyError):
    """Cuando se intenta realizar una operación no permitida."""
    def __init__(self, operation_name: str):
        super().__init__(f"La operación '{operation_name}' no está permitida en esta Company.")        


class CompanyPermissionError(CompanyError):
    """Cuando el usuario no tiene permisos para modificar o acceder."""
    def __init__(self):
        super().__init__("No tienes permisos para realizar esta acción sobre la Company.")      
