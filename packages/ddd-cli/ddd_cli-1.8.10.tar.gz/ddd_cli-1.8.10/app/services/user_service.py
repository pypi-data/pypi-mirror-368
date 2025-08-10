
"""
Los servicios en DDD son responsables de manejar la lógica de negocio 
y las operaciones CRUD relacionadas con una entidad específica. 
Este servicio proporciona métodos para listar, contar, crear, recuperar, actualizar y eliminar instancias de la entidad user. 
Cada método maneja la validación necesaria y utiliza un repositorio para interactuar con la persistencia de datos.
son utiles para:
- Centralizar la lógica de negocio relacionada con una entidad.
- Facilitar la reutilización de código en diferentes partes de la aplicación.
- Proporcionar una interfaz clara para interactuar con las entidades.
- Facilitar la implementación de patrones como CQRS (Command Query Responsibility Segregation).
- Permitir la separación de preocupaciones entre la lógica de negocio y la persistencia de datos.
- Facilitar la implementación de pruebas unitarias y de integración.
- Facilitar la gestión de transacciones y la consistencia de datos.
- Permitir la implementación de reglas de negocio complejas que pueden involucrar múltiples entidades o servicios.
- Facilitar la implementación de patrones de diseño como el patrón de servicio, unidad de trabajo, repositorio, etc.
- Proporcionar una interfaz coherente para interactuar con diferentes tipos de almacenamiento de datos (por ejemplo, bases de datos, servicios web, etc.).
"""

from typing import List, Optional

# importa las entidades utilizadas aqui
from ..domain.entities import UserEntity

# importa las excepciones utilizadas aqui
from ..domain.exceptions import (
    UserValueError,
    UserValidationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserOperationNotAllowedError,
    UserPermissionError
)
from ..infrastructure.exceptions import RepositoryError, ConnectionDataBaseError

# importa los repositorios utilizados aqui
from ..infrastructure.user_repository import UserRepository

class UserService:
    """
    Servicio para manejar las operaciones CRUD relacionadas con user.

    Métodos disponibles:
        - list: Lista todas las instancias de user.
        - count_all: Cuenta todas las instancias de user.
        - create: Crea una nueva instancia de user.
        - retrieve: Recupera una instancia de user por ID.
        - update: Actualiza una instancia existente de user.
        - delete: Elimina una instancia de user.
    """

    #Si necesitas mantener un estado de lista de entidades
    # user_list = []    


    def __init__(self, repository: UserRepository):
        """
        Inicializa el servicio con el repositorio correspondiente.

        params:
            repository: Repositorio que maneja la persistencia de user.
        """

        self.repository = repository    


    def list(self, filters: Optional[dict] = None) -> List[dict]:
        """
        Lista instancias de user.

        params:
            filters: Filtros opcionales para la consulta.
        return: 
            Lista de la entidad
        raises:
            UserValueError:  Si el valor de entrada no es válido.
            ConnectionDataBaseError: Si hay un error al conectar a la base de datos.
            RepositoryError: Si ocurre un error inesperado (interno del sistema).
        """

        entity_list = self.repository.get_all(filters=filters)

        return [entity.to_dict() for entity in entity_list]      


    def count_all(self, filters: Optional[dict] = None) -> int:
        """
        Cuenta todas las instancias de user.

        param: 
            filters: Filtros opcionales para la consulta.
        return: 
            Número total de instancias.
        raises: 
            UserValueError:  Si el valor de entrada no es válido.
            ConnectionDataBaseError: Si ocurre un error al acceder a la base de datos.       
            RepositoryError: Si ocurre un error inesperado (interno del sistema).             
        """

        return self.repository.count_all(filters=filters)


    def create(self, data, external_id: Optional[int]=None, externals: Optional[List[int]]=None, adicionalData=None) -> dict:
        """
        Crea una nueva instancia de user.

        params: 
            data: Diccionario o DTO con los datos necesarios para crear la instancia.
            external_id: ID del padre si es necesario (opcional).
            externals: Lista de IDs de entidades relacionadas (opcional).
            adicionalData: Datos adicionales a incluir en la creación.
        return: 
            La entidad creada.
        raises: 
            UserValueError: Si el valor de entrada no es válido.
            UserValidationError: Si los datos no son válidos.
            UserAlreadyExistsError: Si ya existe un registro con el mismo nombre.            
            ConnectionDataBaseError: Si ocurre un error al acceder a la base de datos.
            RepositoryError: Si ocurre un error inesperado (interno del sistema).            
        """

        # Validación de reglas de negocio (opcional)
        if self.repository.exists_by_field(field_name="attributeName", value=data['attributeName']):
            raise UserValueError(field="attributeName", detail="An instance with this attributeName already exists")

        #crear y validar la entidad
        entity = UserEntity.from_dict(data)
        entity.validate()       

        # Guardar en el repositorio
        saved_entity = self.repository.create(entity=entity, external_id=external_id, externals=externals, adicionalData=adicionalData)

        return saved_entity.to_dict()


    def retrieve(self, entity_id: int) -> dict:
        """
        Recupera una instancia de user por su ID.

        param: 
            entity_id: ID de la instancia a recuperar.
        return: 
            La entidad recuperada.
        raises:
            UserValueError: Si el valor de entrada no es válido.         
            UserNotFoundError: Si no existe el registro con el ID dado.
            ConnectionDataBaseError: Si ocurre un error al acceder a la base de datos.
            RepositoryError: Si ocurre un error inesperado (interno del sistema).
        """

        entity = self.repository.get_by_id(id=entity_id)

        return entity.to_dict()


    def update(self, entity_id: int, data, external_id: Optional[int]=None, externals: Optional[List[int]]=None,adicionalData=None) -> dict:
        """
        Actualiza una instancia existente de user.

        params:
            entity_id: ID de la instancia a actualizar.
            data: Diccionario o DTO con los datos a actualizar.
            external_id: ID del padre si es necesario (opcional).
            externals: Lista de IDs de entidades relacionadas (opcional).
            adicionalData: Datos adicionales a incluir en la actualización.
        return: 
            La entidad actualizada.
        raises: 
            UserNotFoundError: Si no existe el registro con el ID dado.
            UserValueError: Si el valor de entrada no es válido.                 
            UserValidationError: Si los datos no son válidos.            
            ConnectionDataBaseError: Si ocurre un error al acceder a la base de datos.
            RepositoryError: Si ocurre un error inesperado (interno del sistema).
        """

        # Recuperar la entidad
        entity = self.repository.get_by_id(id=entity_id)

        # actualizar la instancia y validar
        entity.update(data)     
        entity.validate()   

        # Guardar en el repositorio
        updated_entity = self.repository.update(entity=entity, external_id=external_id, externals=externals, adicionalData=adicionalData)

        return updated_entity.to_dict()


    def delete(self, entity_id: int) -> bool:
        """
        Elimina una instancia de user.

        params:
            entity_id: ID de la instancia a eliminar.
        return: 
            True/False (depende del exito de la operacion)
        raises:
            UserNotFoundError: Si no se encuentra la instancia.
            UserValueError: Si el valor de entrada no es válido.
            UserValidationError: Si los datos no son válidos.            
            ConnectionDataBaseError: Si ocurre un error al acceder a la base de datos.
            RepositoryError: Si ocurre un error inesperado (interno del sistema).            
        """
        
        # Verifica si la entidad existe
        if not self.repository.exists_by_field(field_name="id", value=entity_id):
            raise UserNotFoundError(id=entity_id)

        # Eliminación en el repositorio
        self.repository.delete(id=entity_id)

        return True
