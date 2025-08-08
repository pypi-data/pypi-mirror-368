def clean_dict_of_keys(data: dict, keys=()) -> dict:
    """
    Limpia un diccionario eliminando claves específicas.

    Args:
        data (dict): El diccionario a limpiar.
        keys (list): Lista de claves a eliminar del diccionario.

    Returns:
        dict: Un nuevo diccionario sin las claves especificadas.
    """
    return {k: v for k, v in data.items() if k not in keys}
