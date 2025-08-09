import calendar
import logging
from datetime import datetime

import pytz
from vlcishared.utils.date_format import convertir_fecha_a_tz

from gestion_fechas.proceso_etl import ProcesoETL
from gestion_fechas.repositorio import GestionFechasRepositorio
from gestion_fechas.utils.excepciones import ETLEnProcesoError, ETLNoRegistradaError
from gestion_fechas.utils.fechas_utils import mapear_formato_personalizado
from gestion_fechas.utils.validador import ESTADOS_POSIBLES, validar_estado, validar_fecha, validar_fecha_ETL, validar_intervalo


class GestionFechasServicio:
    """
    Servicio encargado de la lógica de negocio para la gestión de fechas de ETLs.
    """

    def __init__(self, etl_nombre: str, tz: str):
        """
        Inicializa el servicio con el repositorio de gestión de fechas.

        Args:
            - etl_nombre (str): Nombre de la ETL.
            - tz (str): Zona horaria en formato reconocido por pytz. Valor por defecto "Europe/Madrid".

        """
        self.log = logging.getLogger(__name__)
        self.repositorio = GestionFechasRepositorio(etl_nombre)
        self.tz = pytz.timezone(tz)

    def tiene_gestion_de_fechas(self) -> bool:
        """
        Determina si en la tabla de gestión de fechas existe una ETL con el nombre recibido.

        Returns:
            bool: True si corresponde a una ETL con gestión de fechas, False en caso contrario.

        Raises:
            Exception: Si ocurrió un error inesperado al consultar la gestión de fechas.
        """
        try:
            self.repositorio.obtener_datos_etl(self.tz)
            return True
        except ETLNoRegistradaError:
            self.log.info(f"La ETL '{self.repositorio.etl_nombre}' no tiene gestión de fechas.")
            return False
        except Exception as e:
            self.log.info(f"Error al consultar gestión de fechas de la etl: {e}")
            raise

    def es_necesaria_ejecucion(self, campo_fecha: str) -> bool:
        """
        Determina si se deben recuperar datos según el estado y el campo de fecha indicado.

        Args:
            campo_fecha (str): Nombre del atributo de fecha a comparar ('fen', 'fen_fin').

        Returns:
            bool: True si corresponde recuperar datos, False en caso contrario.

        Raises:
            Exception: Si el estado o la fecha son inválidos.
        """
        try:
            proceso_etl = self.repositorio.refrescar_datos_etl(self.tz)
            self.log.info(
                f"Verificando si es necesaria la ejecución para ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id}. Estado: '{proceso_etl.estado}'."
            )
            validar_estado(proceso_etl.estado)

            if proceso_etl.estado == "EN PROCESO":
                raise ETLEnProcesoError(proceso_etl.etl_nombre, proceso_etl.etl_id)

            elif proceso_etl.estado == "ERROR":
                return True

            fecha_valor = getattr(proceso_etl, campo_fecha, None)
            validar_fecha_ETL(fecha_valor, campo_fecha)
            fecha_valor = convertir_fecha_a_tz(fecha_valor, pytz.timezone("Europe/Madrid"))

            fecha_limite = datetime.now(pytz.timezone("Europe/Madrid"))

            if proceso_etl.offset:
                validar_intervalo(proceso_etl.offset, "offset")
                fecha_limite -= proceso_etl.offset

            # Se evalúa si la frecuencia es mayor o igual a un día: se compara solo la fecha (sin hora)
            if proceso_etl.frecuencia.years >= 1 or proceso_etl.frecuencia.months >= 1 or proceso_etl.frecuencia.days >= 1:
                ejecutar = fecha_valor.date() < fecha_limite.date()
            else:
                ejecutar = fecha_valor < fecha_limite

            if ejecutar:
                self.log.info(f"Es necesaria la ejecución de la etl {proceso_etl.etl_nombre}.")
            else:
                self.log.info(f"No es necesaria la ejecución de la etl {proceso_etl.etl_nombre}.")

            return ejecutar
        except ETLEnProcesoError:
            raise
        except Exception as e:
            self.log.exception(f"Error al evaluar necesidad de recuperar datos: {e}")
            raise

    def obtener_formato_fecha(self) -> str:
        """
        Obtiene y retorna el formato de la fecha de la ETL en formato en uno compatible con las funciones de fechas en Python

        Returns:
            - str: Formato de fecha fen.
        """
        try:
            proceso_etl = self.repositorio.obtener_datos_etl(self.tz)
            if proceso_etl.formato_fen:
                formato_mapeado = mapear_formato_personalizado(proceso_etl.formato_fen)
            else:
                formato_mapeado = "%Y-%m-%dT%H:%M:%S%z"

            return formato_mapeado

        except Exception as e:
            self.log.exception(f"Error al obtener el formato de fecha: {e}")
            raise

    def obtener_fecha_fen_a_procesar(self) -> datetime:
        """
        Obtiene y retorna la fecha fen para la ejecución de la ETL.

        Returns:
            - datetime: Fecha fen.

        Raises:
            - Exception: Si no existe fecha válida.
        """
        try:
            proceso_etl = self.repositorio.obtener_datos_etl(self.tz)
            self.log.info(f"Obteniendo fecha de gestión (fen) para ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id}.")
            validar_fecha_ETL(proceso_etl.fen, "fen")

            return proceso_etl.fen
        except Exception as e:
            self.log.exception(f"Error al obtener fecha de gestión: {e}")
            raise

    def obtener_rango_fechas_a_procesar(self) -> dict[str, datetime]:
        """
        Obtiene las fechas fen_inicio y fen_fin para la ejecución de la ETL y las retorna.

        Returns:
            - dict[str, datetime]: Rango de fechas fen_inicio y fen_fin.

        Raises:
            - Exception: Si no existen fechas válidas.
        """
        try:
            proceso_etl = self.repositorio.obtener_datos_etl(self.tz)
            self.log.info(f"Obteniendo fechas de gestión (fen_inicio y fen_fin) para ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id}.")
            validar_fecha_ETL(proceso_etl.fen_inicio, "fen_inicio")
            validar_fecha_ETL(proceso_etl.fen_fin, "fen_fin")
            return {
                "fen_inicio": proceso_etl.fen_inicio,
                "fen_fin": proceso_etl.fen_fin,
            }
        except Exception as e:
            self.log.exception(f"Error al obtener rango de fechas de gestión: {e}")
            raise

    def actualizar_estado_etl(self, nuevo_estado: str) -> None:
        """
        Actualiza el estado de la ETL.

        Args:
            - nuevo_estado (str): Estado a establecer. Debe ser "OK", "EN PROCESO" o "ERROR".

        Raises:
            - Exception: Si el estado no es válido o falla la actualización.
        """
        try:
            proceso_etl = self.repositorio.obtener_datos_etl(self.tz)
            self.log.info(f"Actualizando estado de ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id} a '{nuevo_estado}'.")

            if nuevo_estado not in ESTADOS_POSIBLES:
                raise Exception(f"El estado recibido: '{nuevo_estado}' no es un estado válido.")

            self.repositorio.actualizar_estado_etl(nuevo_estado)
        except Exception as e:
            self.log.exception(f"Error al actualizar estado a '{nuevo_estado}': {e}")
            raise

    def calcular_y_actualizar_siguiente_fen(self) -> None:
        """
        Calcula y actualiza la siguiente fecha de procesamiento (fen) según la frecuencia.

        Raises:
            - Exception: Si el estado actual es inválido o faltan fechas.
        """
        try:
            proceso_etl = self.repositorio.obtener_datos_etl(self.tz)
            self.log.info(f"Calculando siguiente fecha fen para ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id}.")

            self._calcular_y_actualizar_fecha(proceso_etl, "fen")
        except Exception as e:
            self.log.exception(f"Error al calcular la siguiente fecha fen: {e}")
            raise

    def calcular_y_actualizar_siguiente_rango(self) -> None:
        """
        Calcula y actualiza la siguiente fecha de procesamiento de los campos fen_inicio y fen_fin según la frecuencia.

        Raises:
            - Exception: Si el estado actual es inválido o faltan fechas.
        """
        try:
            proceso_etl = self.repositorio.obtener_datos_etl(self.tz)
            self.log.info(f"Calculando siguiente rango de fechas para ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id}.")

            self._calcular_y_actualizar_fecha(proceso_etl, "fen_inicio")
            self._calcular_y_actualizar_fecha(proceso_etl, "fen_fin")
        except Exception as e:
            self.log.exception(f"Error al calcular el siguiente rango de fechas: {e}")
            raise

    def _calcular_y_actualizar_fecha(self, proceso_etl: ProcesoETL, campo: str):
        fecha_gestion = getattr(proceso_etl, campo)
        frecuencia = proceso_etl.frecuencia
        validar_fecha_ETL(fecha_gestion, campo)
        validar_intervalo(frecuencia, "frecuencia")

        # Se elimina la zona horaria (fecha naive) para evitar errores al sumar períodos (días/meses/horas),
        # ya que las operaciones de RelativeDelta no siempre se comportan bien con datetimes con tzinfo.

        fecha_naive = fecha_gestion.replace(tzinfo=None)
        nueva_fecha_naive = fecha_naive + frecuencia

        # Si la fecha original era el último día del mes, se fuerza que la nueva fecha también lo sea,
        # para evitar inconsistencias al sumar meses (ej. sumar 1 mes a 30 de abril da 31 de mayo).
        _, last_day_fecha_gestion = calendar.monthrange(fecha_gestion.year, fecha_gestion.month)
        es_ultimo_dia = fecha_gestion.day == last_day_fecha_gestion

        if es_ultimo_dia and frecuencia.months > 0:
            _, last_day_nuevo_mes = calendar.monthrange(nueva_fecha_naive.year, nueva_fecha_naive.month)
            nueva_fecha_naive = nueva_fecha_naive.replace(day=last_day_nuevo_mes)

        nueva_fecha = self.tz.localize(nueva_fecha_naive)
        validar_fecha(fecha_gestion, campo)

        self.repositorio.actualizar_fecha_etl(campo, nueva_fecha)
        self.log.info(f"Nueva fecha '{campo}' actualizada a: {nueva_fecha}")

    def actualizar_fecha(self, campo: str, nueva_fecha: datetime):
        validar_fecha(nueva_fecha, campo)
        nueva_fecha = convertir_fecha_a_tz(nueva_fecha, self.tz)

        self.repositorio.actualizar_fecha_etl(campo, nueva_fecha)
        self.log.info(f"Nueva fecha '{campo}' actualizada a: {nueva_fecha}")
