import logging
from datetime import datetime

from sqlalchemy import text
from vlcishared.db.postgresql import PostgresConnector
from vlcishared.utils.date_format import convertir_fecha_a_tz

from gestion_fechas.proceso_etl import ProcesoETL
from gestion_fechas.utils.excepciones import ETLNoRegistradaError
from gestion_fechas.utils.fechas_utils import parsear_intervalo_postgres_a_relativedelta


class GestionFechasRepositorio:
    """
    Repositorio para acceder a funciones SQL relacionadas con la gestión de fechas para ETLs.
    """

    def __init__(self, etl_nombre: str):
        """
        Inicializa el repositorio y guarda el nombre de la ETL.

        Args:
            etl_nombre (str): Nombre de la ETL.

        Raises:
            Exception: Si falla la conexión o carga del proceso ETL.
        """
        self.log = logging.getLogger(__name__)
        try:
            self.conector_db = PostgresConnector.instance()
        except Exception as e:
            self.log.error("GestionFechas requiere que PostgresConnector esté inicializado previamente.")
            raise e
        self.etl_nombre = etl_nombre
        self.proceso_etl = None

    def obtener_datos_etl(self, tz) -> ProcesoETL:
        """
        Obtiene los datos de gestión de fechas de la ETL.

        Returns:
            ProcesoETL: Datos de la ETL.

        Raises:
            ValueError: Si la ETL no existe.
        """
        if self.proceso_etl:
            return self.proceso_etl
        else:
            return self.refrescar_datos_etl(tz)

    def refrescar_datos_etl(self, tz) -> ProcesoETL:
        """
        Obtiene los datos de gestión de fechas de la ETL desde la base de datos.

        Returns:
            ProcesoETL: Datos de la ETL.

        Raises:
            ValueError: Si la ETL no existe.
        """
        self.log.info(f"Obteniendo datos de gestión de fechas de la ETL '{self.etl_nombre}' desde la base de datos.")

        resultado = self.conector_db.execute(
            text(
                """SELECT etl_id, etl_nombre, estado, frecuencia::text AS frecuencia_text, "offset"::text as offset_text, fen, fen_inicio, fen_fin, formato_fen
                FROM vlci2.t_ref_gestion_fechas_etls WHERE etl_nombre = :etl_nombre"""
            ),
            {"etl_nombre": self.etl_nombre},
        )

        fila = resultado.mappings().first()

        if not fila:
            raise ETLNoRegistradaError(self.etl_nombre)

        self.proceso_etl = ProcesoETL(
            etl_id=fila["etl_id"],
            etl_nombre=fila["etl_nombre"],
            frecuencia=parsear_intervalo_postgres_a_relativedelta(fila["frecuencia_text"]),
            offset=parsear_intervalo_postgres_a_relativedelta(fila["offset_text"]),
            fen=convertir_fecha_a_tz(fila["fen"], tz),
            fen_inicio=convertir_fecha_a_tz(fila["fen_inicio"], tz),
            fen_fin=convertir_fecha_a_tz(fila["fen_fin"], tz),
            formato_fen=fila["formato_fen"],
            estado=fila["estado"],
        )

        return self.proceso_etl

    def actualizar_estado_etl(self, nuevo_estado: str) -> None:
        """
        Actualiza el estado de gestión de fechas de la ETL.

        Args:
            nuevo_estado (str): El nuevo estado ("OK", "EN PROCESO", "ERROR").
        """
        self.log.info(f"Actualizando el estado de la ETL '{self.etl_nombre}' a '{nuevo_estado}' en la base de datos.")
        self.conector_db.execute(
            text("UPDATE vlci2.t_ref_gestion_fechas_etls SET estado = :estado WHERE etl_id = :etl_id"),
            {
                "estado": nuevo_estado,
                "etl_id": self.proceso_etl.etl_id,
            },
        )

    def actualizar_fecha_etl(self, campo: str, nueva_fecha: datetime) -> None:
        """
        Actualiza un campo de fecha de la ETL.

        Args:
            campo (str): Nombre del campo de fecha.
            nueva_fecha (datetime): Nueva fecha a establecer.

        Raises:
            ValueError: Si el campo no es válido.
        """
        if campo not in ["fen", "fen_inicio", "fen_fin"]:
            raise ValueError(f"Campo con nombre {campo} no corresponde a un campo de fecha.")

        self.log.info(f"Actualizando el campo '{campo}' de la ETL '{self.etl_nombre}' a '{nueva_fecha}' en la base de datos.")
        self.conector_db.execute(
            text(f"UPDATE vlci2.t_ref_gestion_fechas_etls SET {campo} = :nueva_fecha WHERE etl_id = :etl_id"),
            {
                "nueva_fecha": nueva_fecha,
                "etl_id": self.proceso_etl.etl_id,
            },
        )
