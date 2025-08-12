from datetime import datetime, timedelta
import json
import os
from acelerai_inputstream.models.inputstream import Inputstream
from acelerai_inputstream.utils import CustomJSONEncoder, CustomJsonDecoder, load_full_object
import logging
logger = logging.getLogger("CacheManager")


class CacheManager:
    duration_inputstream:int
    duration_data:int

    def __init__(self, cache_options: dict | None = None):
        if cache_options is None:
            self.duration_data = 60 * 24
            self.duration_inputstream = 60 * 24
        else:
            self.duration_data = cache_options.get("duration_data", 60 * 24)
            self.duration_inputstream = cache_options.get("duration_inputstream", 60 * 24)

        # create cache directories
        if not os.path.exists(".acelerai_cache"):
            os.mkdir(".acelerai_cache")
            os.mkdir(".acelerai_cache/data")
        
        
    def get_inputstream(self, ikey:str) -> Inputstream | None:
        """
        return Inputstream if exists in cache and is not expired
        otherwise return None
        params:
            ikey: str
        """
        file_name = f".acelerai_cache/inputstreams/{ikey}.json"
        if os.path.exists(file_name):
            logger.info(f"Inputstream - Ikey: {ikey}, Checking cache expiration...")
            data = json.loads(open(file_name, "r").read(), cls=CustomJsonDecoder)
            if datetime.utcnow() < data["duration"]:
                logger.info(f"Inputstream - Ikey: {ikey}, from cache")
                return Inputstream(**data["inputstream"])
            else:
                logger.info(f"Inputstream - Ikey: {ikey}, Cache expired, removing file...")
                os.remove(file_name)
                return None
        return None


    def set_inputstream(self, inputstream:Inputstream):
        cache_register = {
            "inputstream": inputstream.get_dict(),
            "duration": datetime.utcnow() + timedelta(minutes=self.duration_inputstream)
        }

        file_name = inputstream.Ikey
        if not os.path.exists(f".acelerai_cache/inputstreams/"): os.mkdir(f".acelerai_cache/inputstreams/")
        open(f".acelerai_cache/inputstreams/{file_name}.msgpack", "w+").write(json.dumps(cache_register, cls=CustomJSONEncoder))


    def get_data(self, key:str, hash_query:str) -> list[dict] | None:
        """
        return data if exists in cache and is not expired
        otherwise return None
        params:
            key: str
            query: dict
        """
        file_name = f".acelerai_cache/data/{key}/{hash_query}.msgpack"
        index_ttl_file = f".acelerai_cache/data/ttl_index.json"
        if os.path.exists(file_name) and os.path.exists(index_ttl_file):

            # check if cache is expired
            logger.info(f"Data - Key: {key}, Checking cache expiration...")
            index = json.loads(open(index_ttl_file, "r").read(), cls=CustomJsonDecoder)
            ttl_key = f"{key}_{hash_query}"
            if ttl_key in index:
                ttl = index[ttl_key]
                if datetime.utcnow() > ttl:
                    logger.info(f"Data - Key: {key}, Cache expired, removing file...")
                    os.remove(file_name)
                    return None

            # recover data from cache
            try:
                logger.info(f"Data - Key: {key}, Recovering data from cache...")
                data = load_full_object(file_name)
                logger.info(f"Data - Key: {key}, from cache")
                return data
            except Exception as e:
                if os.path.exists(file_name): os.remove(file_name)
                raise Exception(f"Error reading cache file: {file_name} - {e}", stack_info=True)
        else:
            if os.path.exists(file_name): os.remove(file_name)
            return None
    
    def set_data(self, ikey:str, hash_query:str):
        # update ttl index
        ttl_key = f"{ikey}_{hash_query}"
        ttl = datetime.utcnow() + timedelta(minutes=self.duration_data)
        index_file = f".acelerai_cache/data/ttl_index.json"
        if os.path.exists(index_file):
            index = json.loads(open(index_file, "r").read(), cls=CustomJsonDecoder)
            index[ttl_key] = ttl
            open(index_file, "w+").write(json.dumps(index, cls=CustomJSONEncoder))
        else:
            open(index_file, "w+").write(json.dumps({ttl_key: ttl}, cls=CustomJSONEncoder))