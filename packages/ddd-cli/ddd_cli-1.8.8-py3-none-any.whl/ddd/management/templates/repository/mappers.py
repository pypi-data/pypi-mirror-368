# utils/mappers.py
from dataclasses import asdict, fields
from typing import Type, TypeVar, Any
from django.db import models
from datetime import datetime, date
import decimal
import uuid
from ..domain.exceptions import [[ entity_name.capitalize() ]]ValueError

T = TypeVar("T")

class Mapper:

    @staticmethod
    def entity_to_dict(entity_instance: Any) -> dict:
        """
        Convierte una entidad en un diccionario que contiene solo sus propios campos
        Es exclusivo para el sistema basico DDD (No cambiar)
        """

        # Convertir la entidad a diccionario directamente con asdict (solo los campos de la entidad)
        return asdict(entity_instance)
    

    @staticmethod
    def model_to_entity(model_instance: models.Model, entity_class: Type[T]) -> T:
        """
        Convierte una instancia de modelo Django a una entidad basada solo en los campos de la entidad.
        Es exclusivo para el sistema basico DDD donde las entidades no deben contener datos de otras entidades (No cambiar)

        Conversión según el tipo de propiedad de Django Model:
            CharField -> (str).
            TextField -> (str).
            IntegerField -> (int).
            FloatField -> (float)
            BooleanField -> (bool)
            DateField -> (datetime.date)
            DateTimeField -> (datetime.time)
            ForeignKey -> ID (int/str)
            OneToOneField -> ID (int/str)            
            ManyToManyField -> lista de IDs (int o str)
            DecimalField -> (decimal.Decimal)
            UUIDField -> uuid.UUID
            JSONField -> (dict o list)
            FileField o ImageField -> ruta de archivo(str)
            EmailField -> (str)
            SlugField -> (str)
            AutoField (ID auto-generado) -> (int)
        """

        if not model_instance:
            raise [[ entity_name.capitalize() ]]ValueError("Model instance cannot be None. Cannot convert None to entity")

        entity_field_names = {f.name for f in fields(entity_class)}

        data = {}
        for field_name in entity_field_names:
            if not hasattr(model_instance, field_name):
                continue
            
            try:
                value = getattr(model_instance, field_name)
            except AttributeError:
                continue

            # Manejo especial para diferentes tipos de campo
            if isinstance(value, models.Manager):
                # Para relaciones ManyToMany o reverse FK
                value = list(value.values_list('pk', flat=True)) if value else []

            elif isinstance(value, uuid.UUID):
                # Dejar tal cual; que la entidad lo maneje
                pass

            elif isinstance(value, (datetime, date)):
                # Dejar tal cual; que la entidad lo maneje
                pass

            elif isinstance(value, decimal.Decimal):
                value = float(value)  # o dejar como Decimal si tu entidad lo acepta            

            elif isinstance(value, dict) or isinstance(value, list):
                # JSONField ya devuelve dict/list, dejar intacto
                pass

            elif hasattr(value, 'pk'):
                # Es una relación ForeignKey/OneToOne -> extraer ID
                value = value.pk if value else None

            # Añadir al diccionario solo si es válido
            data[field_name] = value

        return entity_class(**data)
    

    @staticmethod
    def model_to_dict(model_instance: models.Model) -> dict:
        """
        Convierte una entidad de modelo Django a diccionario usando sus campos reales.
        Alternativa segura a asdict().
        Es exclusivo para el sistema basico DDD donde las entidades no deben contener datos de otras entidades (No cambiar)
        """

        data = {}
        for field in model_instance._meta.get_fields():
            try:
                value = getattr(model_instance, field.name)
                
                if isinstance(field, models.ManyToManyField):
                    data[field.name] = list(value.values_list('pk', flat=True))
                elif isinstance(field, models.ForeignKey) and value:
                    data[field.name] = value.pk
                elif isinstance(value, uuid.UUID):
                    data[field.name] = str(value)
                elif isinstance(value, (datetime, date)):
                    data[field.name] = value
                else:
                    data[field.name] = value
            except AttributeError:
                continue  # Algunos campos virtuales pueden no estar disponibles
        return data

"""
Si necesitas obtener mas detalles sobre una instancia de tu model a parte del ID de las relaciones
recuerda que en un enfoque DDD las entidades no deben contener datos de otras entidades
asi que deberas extender el Mapper para utilizar/generar DTO y asi tus vistas o apis 
ejemplo: 
    #añade un DTO llamdo ListDto

    @dataclass
    class ListDto:
        id: Optional[int] = None  
        title: Optional[str] = None  
        tipo: Optional[str] = None #FK a un model llamado Tipo
        categorias: Optional[List[str]] = None #Relacion con un model llamdo Categorias

        def to_dict(self) -> dict:
            return asdict(self)

    #añade la funcion en tu mapper
    @staticmethod
    def model_to_list_dto(model_instance: models.Model) -> ListDto:
        dto = ListDto()
        dto.id = model_instance.id
        dto.title = model_instance.title
        dto.tipo = model_instance.tipo.nombre if model_instance.tipo else None
        dto.categorias = list(model_instance.categorias.values_list('nombre', flat=True)) if model_instance.categorias else None

llamaras el mapper desde el repositorio pasando el DTO al servicio 
y asi obtendras un DTO con los datos que necesitas en la vista o api

"""

    