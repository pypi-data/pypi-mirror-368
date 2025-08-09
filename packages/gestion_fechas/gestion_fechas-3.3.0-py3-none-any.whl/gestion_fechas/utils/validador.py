from datetime import datetime

from dateutil.relativedelta import relativedelta

ESTADOS_POSIBLES = {"EN PROCESO", "OK", "ERROR"}


def validar_estado(estado):
    if estado not in ESTADOS_POSIBLES:
        raise Exception(f"El estado de la ETL tiene un valor no válido: '{estado}'.")


def validar_fecha(fecha, campo_fecha):
    if not fecha or not isinstance(fecha, datetime):
        raise Exception(f"La nueva fecha recibida para el campo '{campo_fecha}' no es válida: '{fecha}' ({type(fecha).__name__})")


def validar_fecha_ETL(fecha, campo_fecha):
    if not fecha or not isinstance(fecha, datetime):
        raise Exception(f"La ETL no posee un valor válido en '{campo_fecha}': {fecha} ({type(fecha).__name__})")


def validar_intervalo(intervalo, campo_intervalo):
    if not intervalo or not isinstance(intervalo, relativedelta):
        raise Exception(f"La ETL no posee un valor válido en '{campo_intervalo}': {intervalo} ({type(intervalo).__name__})")
