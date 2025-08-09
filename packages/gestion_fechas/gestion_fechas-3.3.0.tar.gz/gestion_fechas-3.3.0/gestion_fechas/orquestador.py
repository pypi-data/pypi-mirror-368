import logging
from datetime import datetime

import pytz

from gestion_fechas.servicio import GestionFechasServicio


class GestionFechas:
    """
    Clase con métodos orquestadores de gestión de fechas (recuperación automática de las ETLs).
    """

    def __init__(self, etl_nombre: str, tipo: str = "fen", tz: str = "Europe/Madrid"):
        """
        Inicializa la clase orquestadora con el servicio de gestión de fechas.

        Argumentos:
            - etl_nombre (str): Nombre de la ETL.
            - tipo (str): Tipo de fechas manejado en la ETL. Debe ser "fen" o "rango". Valor por defecto "fen".
            - tz (str): Zona horaria en formato reconocido por pytz. Valor por defecto "Europe/Madrid".

        Raises:
            Exception: Si el valor recibido en 'tipo' es incorrecto.
        """
        if tipo not in {"fen", "rango"}:
            raise ValueError(f"Tipo de gestión de fechas no reconocido: {tipo}")

        if tz not in pytz.all_timezones:
            raise ValueError(f"Zona horaria '{tz}' no es válida según pytz.")

        self.log = logging.getLogger(__name__)
        self.etl_nombre = etl_nombre
        self.tipo = tipo
        self.servicio = GestionFechasServicio(etl_nombre, tz)

    def tiene_gestion_de_fechas(self) -> bool:
        """
        Verifica si en la tabla de gestión de fechas existe una ETL con el nombre recibido.

        Retorna:
            - bool: True si la ETL recibida tiene gestión de fechas, False en caso contrario.
        """
        self.log.info(f"Evaluando si existe gestión de fechas para la ETL '{self.etl_nombre}'.")
        return self.servicio.tiene_gestion_de_fechas()

    def es_necesaria_ejecucion(self) -> bool:
        """
        Verifica si es necesario recuperar datos según el estado y fecha de la ETL.

        Retorna:
            - bool: True si hay que recuperar datos, False en caso contrario.
        """
        self.log.info(f"Evaluando si se debe ejecutar ETL '{self.etl_nombre}'")
        if self.tipo == "fen":
            return self.servicio.es_necesaria_ejecucion("fen")
        elif self.tipo == "rango":
            return self.servicio.es_necesaria_ejecucion("fen_fin")

    def obtener_formato_fecha(self) -> str:
        """
        Obtiene y retorna el formato de la fecha de la ETL en un uno compatible con las funciones estándar de fechas en Python strftime/strptime

        Retorna:
            - str: Formato de fecha fen.
        """
        self.log.info(f"Obteniendo formato fecha de la ETL '{self.etl_nombre}'.")
        return self.servicio.obtener_formato_fecha()

    def inicio_gestion_fechas_fen(self) -> datetime:
        """
        Inicia la gestión de fechas, actualizando estado a 'EN PROCESO' y obteniendo la fecha a procesar.

        Retorna:
            - datetime: Fecha a procesar para la ETL.
        """
        self.log.info(f"Iniciando gestión de fechas FEN para ETL '{self.etl_nombre}'.")
        retorno = self.servicio.obtener_fecha_fen_a_procesar()
        self.servicio.actualizar_estado_etl("EN PROCESO")
        return retorno

    def inicio_gestion_fechas_rango(self) -> dict[str, datetime]:
        """
        Inicia la gestión de fechas, actualizando estado a 'EN PROCESO' y obteniendo las fechas a procesar.

        Retorna:
            - dict[str, datetime]: Diccionario con las claves 'fen_inicio' y 'fen_fin', rango de fechas a procesar para la ETL.
        """
        self.log.info(f"Iniciando gestión de fechas rango para ETL '{self.etl_nombre}'.")
        retorno = self.servicio.obtener_rango_fechas_a_procesar()
        self.servicio.actualizar_estado_etl("EN PROCESO")
        return retorno

    def fin_gestion_fechas_OK_fen(self, fen: datetime):
        """
        Finaliza el proceso marcando estado 'OK' y avanza la fecha (fen) a la fecha recibida.
        """
        self.log.info(f"Fin gestión de fechas OK para ETL '{self.etl_nombre}'.")
        if self.tipo == "fen":
            self.servicio.actualizar_fecha("fen", fen)
        elif self.tipo == "rango":
            raise Exception("El campo fen no corresponde a la ETL en curso, que espera un rango (fen_inicio y fen_fin).")

        self.servicio.actualizar_estado_etl("OK")

    def fin_gestion_fechas_OK_rango(self, fen_inicio: datetime, fen_fin: datetime):
        """
        Finaliza el proceso marcando estado 'OK' y avanza las fechas del rango (fen_inicio y fen_fin) a las fechas recibidas.
        """
        self.log.info(f"Fin gestión de fechas OK para ETL '{self.etl_nombre}'.")
        if self.tipo == "fen":
            raise Exception("Los campos fen_inicio y fen_fin no corresponden a la ETL en curso, que espera solo una fecha (fen).")
        elif self.tipo == "rango":
            self.servicio.actualizar_fecha("fen_inicio", fen_inicio)
            self.servicio.actualizar_fecha("fen_fin", fen_fin)

        self.servicio.actualizar_estado_etl("OK")

    def fin_gestion_fechas_OK(self):
        """
        Finaliza el proceso marcando estado 'OK', calcula y avanza la fecha (fen) o rango (fen_inicio y fen_fin) según el tipo de la ETL.
        """
        self.log.info(f"Fin gestión de fechas OK para ETL '{self.etl_nombre}'.")
        if self.tipo == "fen":
            self.servicio.calcular_y_actualizar_siguiente_fen()
        elif self.tipo == "rango":
            self.servicio.calcular_y_actualizar_siguiente_rango()

        self.servicio.actualizar_estado_etl("OK")

    def fin_gestion_fechas_KO(self) -> None:
        """
        Finaliza el proceso marcando estado 'ERROR' sin avanzar la fecha.
        """
        self.log.info(f"Fin gestión de fechas KO para ETL '{self.etl_nombre}'.")
        self.servicio.actualizar_estado_etl("ERROR")
