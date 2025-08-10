
# domain/exceptions.py

class UserError(Exception):
    """Excepción base para errores relacionados con el dominio User."""
    pass


class UserValueError(UserError):
    """Error de valor en atributos de la entidad User."""
    def __init__(self, detail: str, field: str = "value"):
        self.field = field
        self.detail = detail
        if field == "value":
            super().__init__(f"Error de valor: {detail}")
        else:
            super().__init__(f"Error en el campo '{field}': {detail}")


class UserValidationError(UserError):
    """Errores de validación de datos antes de guardar el modelo."""
    def __init__(self, errors):
        self.errors = errors
        super().__init__("La validación de la User falló.")


class UserAlreadyExistsError(UserError):
    """Cuando se intenta crear una User que ya existe."""
    def __init__(self, detail: str, field: str = "value"):
        self.field = field        
        self.detail = detail
        super().__init__(f"User existe.")


class UserNotFoundError(UserError):
    """Cuando se intenta acceder a una User inexistente."""
    def __init__(self, id):
        self.id = id
        super().__init__(f"User con ID {id} no encontrada.")


class UserOperationNotAllowedError(UserError):
    """Cuando se intenta realizar una operación no permitida."""
    def __init__(self, operation_name: str):
        super().__init__(f"La operación '{operation_name}' no está permitida en esta User.")        


class UserPermissionError(UserError):
    """Cuando el usuario no tiene permisos para modificar o acceder."""
    def __init__(self):
        super().__init__("No tienes permisos para realizar esta acción sobre la User.")      
