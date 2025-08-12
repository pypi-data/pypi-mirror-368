from datetime import date, datetime
from enum import Enum
import json
import math
from uuid import UUID
import msgpack
from decimal import Decimal
from dateutil import parser

import logging
logger = logging.getLogger("AcelerUtil")

def custom_encoder(obj):
    if isinstance(obj, datetime) or isinstance(obj, date):
        return obj.isoformat()
        
    if isinstance(obj, Decimal):
        return float(obj)
    
    raise TypeError(f"Object of type {type(obj).__name__} is not serializable")


def decode_datetime(obj:dict):
    for k, v in obj.items():
        if isinstance(v, str) and 'T' in v and '-' in v and ':' in v and len(v) < 35:
            try:
                dv = parser.parse(v)
                dt = dv.replace(tzinfo=None)
                obj[k] = dt
            except: pass

        elif isinstance(v, str) and '-' in v and len(v) < 11:
            try:
                obj[k] = parser.parse(v).date()
                if 'T' in v and '-' in v and ':' in v and len(v) < 40:
                    obj[k] = datetime.fromisoformat(v)
                elif '-' in v and len(v) < 11:
                    obj[k] = parser.parse(v)
            except ValueError:
                pass

    return obj


def load_full_object(file_path):
    """Carga completamente el objeto desde un archivo MessagePack en memoria. Cargar todos los registros en memoria como una lista de diccionarios."""
    try:
        with open(file_path, "rb") as file:
            unpacker = msgpack.Unpacker(file, raw=False, object_hook=decode_datetime)
            data = [record for record in unpacker]
        return data
    except Exception as e:
        logger.error(f"Error al cargar el archivo: {e}", exc_info=True)
        return None
    

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and math.isnan(obj):
            return None
        
        elif obj is None:
            return None
        
        elif isinstance(obj, Enum):
            return obj.value
        
        elif isinstance(obj, datetime):
            return obj.isoformat()
        
        elif isinstance(obj, date):
            #logger.debug(f"Date: {obj}")
            #return datetime.strptime(obj, "%Y-%m-%d").date()
            return obj.isoformat()
        
        elif isinstance(obj, UUID):
            return str(obj)
        else:
            return super().default(obj)


class CustomJsonDecoder(json.JSONDecoder):
    def __init__(self, *args ,**kargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kargs)

    def object_hook(self, obj:dict):
        for k, v in obj.items():
            if isinstance(v, str) and 'T' in v and '-' in v and ':' in v and len(v) < 40:
                try:
                    dv = parser.parse(v)
                    dt = dv.replace(tzinfo=None)
                    obj[k] = dt
                except:
                    pass
            elif isinstance(v, str) and '-' in v and len(v) < 11:
                try:
                    obj[k] = parser.parse(v).date()
                except:
                    pass
        return obj



