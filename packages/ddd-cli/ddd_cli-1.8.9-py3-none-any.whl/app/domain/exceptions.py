
# domain/exceptions.py

class ShorturlError(Exception):
    """Excepción base para errores relacionados con el dominio Shorturl."""
    pass


class ShorturlValueError(ShorturlError):
    """Error de valor en atributos de la entidad Shorturl."""
    def __init__(self, detail: str, field: str = "value"):
        self.field = field
        self.detail = detail
        if field == "value":
            super().__init__(f"Error de valor: {detail}")
        else:
            super().__init__(f"Error en el campo '{field}': {detail}")


class ShorturlValidationError(ShorturlError):
    """Errores de validación de datos antes de guardar el modelo."""
    def __init__(self, errors):
        self.errors = errors
        super().__init__("La validación de la Shorturl falló.")


class ShorturlAlreadyExistsError(ShorturlError):
    """Cuando se intenta crear una Shorturl que ya existe."""
    def __init__(self, cause):
        self.cause = cause
        super().__init__(f"Shorturl existe.")


class ShorturlNotFoundError(ShorturlError):
    """Cuando se intenta acceder a una Shorturl inexistente."""
    def __init__(self, id):
        self.id = id
        super().__init__(f"Shorturl con ID {id} no encontrada.")


class ShorturlOperationNotAllowedError(ShorturlError):
    """Cuando se intenta realizar una operación no permitida."""
    def __init__(self, operation_name: str):
        super().__init__(f"La operación '{operation_name}' no está permitida en esta Shorturl.")        


class ShorturlPermissionError(ShorturlError):
    """Cuando el usuario no tiene permisos para modificar o acceder."""
    def __init__(self):
        super().__init__("No tienes permisos para realizar esta acción sobre la Shorturl.")      
