@dataclass
class [[ dto_name.capitalize() ]]Dto:
    """
    Data Transfer Object para [[ dto_name.lower() ]].

    Este DTO se utiliza para transferir datos entre capas del sistema, 
    como entre la capa de dominio y la capa de infraestructura o vistas.
    """

    # identificadores
    id: Optional[int] = None  # ID es opcional al crear un nuevo objeto

    # Atributos principales
    attributeName: str  # Atributo obligatorio
    attributeEmail: Optional[str] = None  # Atributo opcional

    # Relaciones
    external_id: Optional[int] = None  # ID de la entidad externa asociada (ideal para relaciones 1-a-1)
    externals: Optional[List[int]] = None  # Lista de IDs de entidades relacionadas (ideal para relaciones 1-a-M o M-a-M)


    def __post_init__(self):
        self.validate()       


    def validate(self) -> None:
        """
        Valida los datos del DTO.
        Transporte y validación básica de datos
        - Validaciones centradas en un conjunto específico de datos (integridad de datos)
        - Ejemplo: campos no nulos, longitud mínima
        """


    def to_dict(self) -> dict:
        """
        Convierte el DTO a un diccionario.
        Ideal para serialización.
        """
        return self.__dict__


    @staticmethod
    def from_dict(data: dict) -> "[[ dto_name.capitalize() ]]Dto":
        """
        Crea una instancia del DTO a partir de un diccionario.
        """
        return [[ dto_name.capitalize() ]]Dto(**data)


    '''
    Ejemplos de: 

    - Atributos obligatorios y opcionales
        name: str  # Nombre obligatorio
        email: Optional[str] = None  # Email opcional
        slug: Optional[str] = None  # Identificador único legible para URLs
        content: Optional[str] = None  # Contenido detallado o descripción extensa
        price: Optional[float] = None  # Precio o valor numérico
        quantity: Optional[int] = None  # Cantidad disponible o asociada
        rating: Optional[float] = None  # Valoración media (ej. 4.5 estrellas)
        is_active: bool = True  # Estado activo/inactivo
        is_featured: Optional[bool] = None  # Si es destacado/promocionado
        updated_at: Optional[str] = None  # Fecha de última modificación (ISO 8601)
        deleted_at: Optional[str] = None  # Fecha de eliminación o "soft delete"
        image: Optional[str] = None  # URL hacia una imagen asociada
        video: Optional[str] = None  # URL hacia un video asociado
        latitude: Optional[float] = None  # Coordenada de latitud
        longitude: Optional[float] = None  # Coordenada de longitud
        location_name: Optional[str] = None  # Nombre del lugar (dirección o ciudad)
        created_by: Optional[int] = None  # Usuario que creó la entidad
        updated_by: Optional[int] = None  # Usuario que actualizó la entidad
        order_status: Optional[str] = None  # Estado de la orden (e.g., "PENDING", "COMPLETED")
        total_price: Optional[float] = None  # Precio total de la orden
        config: Optional[Dict] = field(default_factory=dict)  # Configuración adicional, ej. {"shipping": "free", "gift_wrap": True} 
        categories: Optional[List[str]] = field(default_factory=list)  # Lista de categorías asociadas, ej. ["electronics", "clothing"]
        items: Optional[List[Dict]] = None  # Lista de artículos asociados ej. [{"product_id": 1, "quantity": 2}, {"product_id": 2, "quantity": 1}]
    
    - Atributos de relación
        external_id: Optional[int] = None  # Identificador externo (ideal para relaciones 1-a-1 con otras entidades o FK)
        external_uuid: Optional[str] = None  # UUID externo
        externals: Optional[List[int]] = None  # Lista de identificadores externos (ideal para relaciones 1-a-M o M-a-M)
        externals_uuids: Optional[List[str]] = None  # Lista de UUIDs externos  

    '''