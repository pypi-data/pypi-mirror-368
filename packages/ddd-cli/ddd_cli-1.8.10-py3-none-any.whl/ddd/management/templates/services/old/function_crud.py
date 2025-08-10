"""
Servicio para manejar las operaciones CRUD relacionadas con [[ entity_name.lower() ]].

Métodos disponibles:
    - list_[[ entity_name.lower() ]]: Lista todas las instancias de [[ entity_name.lower() ]].
    - count_all_[[ entity_name.lower() ]]: Cuenta todas las instancias de [[ entity_name.lower() ]].
    - create_[[ entity_name.lower() ]]: Crea una nueva instancia de [[ entity_name.lower() ]].
    - retrieve_[[ entity_name.lower() ]]: Recupera una instancia de [[ entity_name.lower() ]] por ID.
    - update_[[ entity_name.lower() ]]: Actualiza una instancia existente de [[ entity_name.lower() ]].
    - delete_[[ entity_name.lower() ]]: Elimina una instancia de [[ entity_name.lower() ]].
"""

def list_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, filters: Optional[dict] = None) -> List[dict]:
    """
    Lista instancias de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :return: Lista de la entidad.
    """

    entity_list = repository.get_all(filters=filters)

    return [entity.to_dict() for entity in entity_list]  


def count_all_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, filters: Optional[dict] = None) -> int:
    """
    Cuenta todas las instancias de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param filters: Filtros opcionales para la consulta.
    :return: Número total de instancias.
    """

    return repository.count_all(filters=filters)


def create_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, data, external_id: Optional[int], externals: Optional[List[int]], adicionalData=None) -> dict:
    """
    Crea una nueva instancia de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param data: Diccionario o DTO con los datos necesarios para crear la instancia.
    :param external_id: ID del padre si es necesario (opcional).
    :param externals: Lista de IDs de entidades relacionadas (opcional).
    :param adicionalData: Datos adicionales a incluir en la creación.
    :return: La entidad creada.
    :raises [[ entity_name.capitalize() ]]ValueError: Si las reglas de negocio no se cumplen.
    """

    # Validación de reglas de negocio (opcional)
    if repository.exists_by_field(field_name="attributeName", value=data['attributeName']):
        raise [[ entity_name.capitalize() ]]ValueError(field="attributeName", detail="An instance with this attributeName already exists")

    #crear y validar la entidad
    entity = [[ entity_name.capitalize() ]]Entity.from_dict(data)
    entity.validate()

    # Guardar en el repositorio
    saved_entity = repository.create(entity=entity, external_id=external_id, externals=externals, adicionalData=adicionalData)

    return saved_entity.to_dict()


def retrieve_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, entity_id: int) -> dict:
    """
    Recupera una instancia de [[ entity_name.lower() ]] por su ID.

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param entity_id: ID de la instancia a recuperar.
    :return: La entidad recuperada.
    :raises [[ entity_name.capitalize() ]]NotFoundError: Si no se encuentra la instancia.
    """

    entity = repository.get_by_id(id=entity_id)

    return entity.to_dict()


def update_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, entity_id: int, data, external_id: Optional[int]=None, externals: Optional[List[int]]=None, adicionalData=None) -> dict:
    """
    Actualiza una instancia existente de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param entity_id: ID de la instancia a actualizar.
    :param data: Diccionario o DTO con los datos a actualizar.
    :param external_id: ID del padre si es necesario (opcional).
    :param externals: Lista de IDs de entidades relacionadas (opcional).
    :param adicionalData: Datos adicionales a incluir en la actualización.
    :return: La entidad actualizada.
    :raises [[ entity_name.capitalize() ]]NotFoundError: Si no se encuentra la instancia o las reglas de negocio no se cumplen.
    """

    # Recuperar la entidad
    entity = repository.get_by_id(id=entity_id)
    
    # actualizar la instancia y validar
    entity.update(data)     
    entity.validate()   

    # Guardar en el repositorio
    updated_entity = repository.update(entity=entity, external_id=external_id, externals=externals, adicionalData=adicionalData)

    return updated_entity.to_dict()


def delete_[[ entity_name.lower() ]](repository: [[ entity_name.capitalize() ]]Repository, entity_id: int) -> bool:
    """
    Elimina una instancia de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param entity_id: ID de la instancia a eliminar.
    :return: True/False (depende del exito de la operacion)
    :raises [[ entity_name.capitalize() ]]NotFoundError: Si no se encuentra la instancia.
    """
    
    # Verifica si la entidad existe
    if not repository.exists_by_field(field_name="id", value=entity_id):
        raise [[ entity_name.capitalize() ]]NotFoundError(id=entity_id)

    # Eliminación en el repositorio
    repository.delete(id=entity_id)

    return True