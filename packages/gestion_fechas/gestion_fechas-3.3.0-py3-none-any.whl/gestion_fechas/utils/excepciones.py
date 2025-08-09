class ETLNoRegistradaError(Exception):
    """Excepción lanzada cuando la ETL no está registrada en la base de datos en la tabla de gestión de fechas."""

    def __init__(self, etl_nombre: str):
        super().__init__(f"La ETL con nombre '{etl_nombre}' no está registrada en la gestión de fechas.")


class ETLEnProcesoError(Exception):
    """Excepción lanzada cuando la ETL no está registrada en la base de datos en la tabla de gestión de fechas."""

    def __init__(self, etl_nombre: str, etl_id: str):
        super().__init__(f"El estado de la ETL '{etl_nombre}' con ID: {etl_id} es 'EN PROCESO', no se puede ejecutar.")
