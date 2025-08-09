import re
from datetime import datetime

from dateutil.relativedelta import relativedelta


def parsear_intervalo_postgres_a_relativedelta(intervalo_str):
    """
    Recibe un INTERVAL de postgres en formato str (Ej. "INTERVAL '1 day'") y lo transforma a un relativedelta.
    - Si el intervalo recibido es None, se retorna un relativedelta vacío.
    """
    if not intervalo_str:
        return relativedelta()

    years = months = days = hours = minutes = seconds = 0

    match_year = re.search(r"(\d+)\s+years?", intervalo_str)
    if match_year:
        years = int(match_year.group(1))

    match_month = re.search(r"(\d+)\s+mons?", intervalo_str)
    if match_month:
        months = int(match_month.group(1))

    match_day = re.search(r"(\d+)\s+days?", intervalo_str)
    if match_day:
        days = int(match_day.group(1))

    match_time = re.search(r"(\d+):(\d+):(\d+)", intervalo_str)
    if match_time:
        hours = int(match_time.group(1))
        minutes = int(match_time.group(2))
        seconds = int(match_time.group(3))

    return relativedelta(
        years=years,
        months=months,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
    )


def convertir_string_a_date(fecha, formato):
    """
    Convierte una cadena de texto a un objeto datetime, usando un formato personalizado.
    """
    return datetime.strptime(fecha, formato)


def convertir_date_a_string(fecha, formato):
    """
    Convierte un objeto datetime a una cadena de texto, usando un formato personalizado.
    """
    return fecha.strftime(formato)


def mapear_formato_personalizado(formato: str) -> str:
    """
    Convierte un formato personalizado (por ejemplo: 'DD-MM-YYYY') en uno compatible con las funciones estándar de fechas en Python
    strftime/strptime (por ejemplo: '%d-%m-%Y').

    - `strftime` formatea objetos datetime como cadenas de texto.
    - `strptime` parsea cadenas de texto y las convierte en objetos datetime.
    """
    reemplazo_formatos = {
        "YYYY": "%Y",
        "YY": "%y",
        "MMMM": "%B",
        "MMM": "%b",
        "MM": "%m",
        "DD": "%d",
        "WD": "%A",
        "HH24": "%H",
        "HH12": "%I",
        "HH": "%H",
        "AMPM": "%p",
        "MI": "%M",
        "SS": "%S",
        "TZ": "%z",
    }

    formato = formato.upper()
    for clave, valor in sorted(reemplazo_formatos.items(), key=lambda x: -len(x[0])):
        formato = formato.replace(clave, valor)
    return formato
