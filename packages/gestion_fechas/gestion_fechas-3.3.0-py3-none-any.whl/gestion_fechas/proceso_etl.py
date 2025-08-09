from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta


@dataclass
class ProcesoETL:
    etl_id: int
    etl_nombre: str
    frecuencia: relativedelta
    offset: Optional[relativedelta] = None
    fen: Optional[datetime] = None
    fen_inicio: Optional[datetime] = None
    fen_fin: Optional[datetime] = None
    estado: str = "OK"
    formato_fen: str = None
