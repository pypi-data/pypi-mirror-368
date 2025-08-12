import asyncio
from datetime import datetime
import gzip
import hashlib
import json
import os
import pickle
import struct
import traceback
from acelerai_inputstream.models.asset import Asset
from acelerai_inputstream.models.pagination_data import PaginationData
import httpx
import math
import base64
from httpx import Response
import msgpack
import requests
from acelerai_inputstream import DATA_URL, APIGW, QUERY_MANAGER, VERIFY_HTTPS
from acelerai_inputstream.models.inputstream import INSERTION_MODE, TYPE_OF_RETRY, ExternalDataConnectionDTO, Inputstream
from acelerai_inputstream.utils import CustomJSONEncoder, CustomJsonDecoder, custom_encoder, decode_datetime
import datetime

# Type conversion
from decimal import Decimal
from uuid import UUID

import logging
logger = logging.getLogger("HttpAcelerAI")

SEM = asyncio.Semaphore(20)  # Limitar concurrencia a 20 conexiones
MAX_RETRIES = 5  # Número máximo de reintentos
INITIAL_BACKOFF = 1  # Tiempo inicial de espera en segundos
BACKOFF_MULTIPLIER = 2  # Factor multiplicador para el tiempo de espera

packer = msgpack.Packer(default=custom_encoder) 

class AcelerAIHttpClient():

    def __init__(self, token:str):
        self.token = token
        self.lock = asyncio.Lock()
        
    async def execute_external_command(self, conn_key:str, query:str):
        """
        Execute an external command in the external data connection
        params:
            conn_key: str -> connection key
            query: str -> query/command to execute
        """    
        try:
            headers = {
                "Authorization": f"A2G {self.token}",
                "conn-key": conn_key,
                'Content-Type': 'application/json'
            }
            
            async with httpx.AsyncClient(verify=VERIFY_HTTPS) as client:
                res = await client.post(f"{QUERY_MANAGER}/QueryData/ExecuteExternalCommand", 
                    data=json.dumps(query, cls=CustomJSONEncoder),
                    headers=headers
                )
            
            if res.status_code != 200:
                if res.status_code == 404: raise Exception("ExternalDataConnection not found, please check your connkey")
                if res.status_code == 401: raise Exception("Unauthorized")
                if res.status_code == 403: raise Exception("Forbidden: please check your token or access permissions in the resource")
                raise Exception(f"Error executing external command, {res.status_code} {res.text}")
            
            content = res.json(cls=CustomJsonDecoder)
            
            if not content["success"]: raise Exception(content["errorMessage"])
            logger.info(f"External command executed successfully")
            
            return True
        except Exception as e:
            raise e
        
    async def execute_external_query(self, conn_key:str, query:dict | str, retries_native_is: int = 3, retry_type: TYPE_OF_RETRY = TYPE_OF_RETRY.RETRY_FROM_ERROR) :
        """
        Execute an external query in the external data connection
        params:
            conn_key: str -> connection key
            query: dict | str -> query to execute
        """    
        async with SEM:
            if isinstance(query, dict): query = json.dumps(query, cls=CustomJSONEncoder)
            
            headers = {
                "Authorization": f"A2G {self.token}",
                "conn-key": conn_key,
                'Content-Type': 'application/json'
            }
            
            my_body = { "query": json.dumps(query, cls=CustomJSONEncoder), "retries": retries_native_is, "retry_type": retry_type.value }
            
            timeout = httpx.Timeout(connect=10.0, read=600.0, write=600.0, pool=600.0)
            retries = 0
            backoff = INITIAL_BACKOFF
            try:
                while retries < MAX_RETRIES:
                    async with httpx.AsyncClient(http2=True, verify=VERIFY_HTTPS, timeout=timeout) as client:
                        async with client.stream("POST",f"{QUERY_MANAGER}/QueryData/ExecuteExternalQuery",
                            json=my_body,
                            headers = headers
                        ) as response:
                                """ if response.status_code != 200:
                                    msg = ''
                                    async for chunk in response.aiter_bytes():
                                        if chunk:
                                            msg += chunk.decode("utf-8")
                                    raise Exception(f"{response.status_code} {msg}") """
                                
                                if response.status_code != 200:
                                    if response.status_code == 404: raise Exception("ExternalDataConnection not found, please check your connkey")
                                    if response.status_code == 401: raise Exception("Unauthorized")
                                    if response.status_code == 403: raise Exception("Forbidden: please check your token or access permissions in the resource")
                                    raise Exception(f"Error executing external query, {response.status_code} {response.text}")
                                
                                
                                buffer = b""  # Buffer para ensamblar datos incompletos
                                rows_count = 0
                                attempt_count = 0  # Contador de reintentos
                                async for chunk in response.aiter_bytes():
                                    buffer += chunk
                                    while len(buffer) >= 4:
                                        obj_length = struct.unpack(">I", buffer[:4])[0]
                                        if len(buffer) < 4 + obj_length:
                                            break
                                        obj_data = buffer[4:4 + obj_length]
                                        buffer = buffer[4 + obj_length:]
                                        decompressed_data = gzip.decompress(obj_data)
                                        data = msgpack.unpackb(decompressed_data, object_hook=decode_datetime)
                                        if not isinstance(data, list):
                                            if "acceler_error" in data:
                                                raise Exception(data["message"])    
                                            if "aceler_retry" in data:
                                                logger.info(f"Retrying data download. Retry number {data['retry_count']} of {data['max_retries']}")	
                                                attempt_count += 1
                                            else:
                                                raise Exception("Unexpected data format received, expected a list of dictionaries.")
                                        
                                        if not isinstance(data, list) and "aceler_retry" in data and retry_type == TYPE_OF_RETRY.RETRY_FROM_BEGINNING:           
                                                #eliminar el archivo de cache
                                                query_str = json.dumps(query, cls=CustomJSONEncoder)
                                                query_hash = hashlib.sha256(query_str.encode()).hexdigest()

                                                # vaciar
                                                file_name = f".acelerai_cache/data/{conn_key}/{query_hash}.msgpack"
                                                #vaciar archivo
                                                if os.path.exists(file_name):
                                                    os.remove(file_name)
                                                rows_count = 0   
                                                
                                        if isinstance(data, list):
                                            rows_count += len(data)
                                            if rows_count % 20000 == 0: logger.info(f"Downloaded {rows_count} rows")
                                            
                                            await self._write_to_file(conn_key, query, data)
                                        
                    logger.info(f"Downloaded data on retry {retries}")
                    logger.info(f"total number of attempts to obtain data: {attempt_count}")
                    break  # Si todo va bien, salimos del bucle
                                
            except (httpx.StreamError, httpx.ConnectError, httpx.ReadTimeout) as e:
                # Manejar errores específicos de conexión y reinicio
                retries += 1
                if retries >= MAX_RETRIES:
                    raise Exception(f"Max retries exceeded: {e}")
                logger.warning(f"Error: {e}. Retrying in {backoff} seconds...")
                await asyncio.sleep(backoff)
                backoff *= BACKOFF_MULTIPLIER  # Incrementar el tiempo de espera exponencialmente
            

    def get_external_data_conn_by_connkey(self, connkey:str) -> ExternalDataConnectionDTO:
        """
        Get external data connection by connkey
        params:
            connkey: str -> connection key
        """
        try:
            headers = { "Authorization": f"A2G {self.token}"}
            res = requests.get(APIGW + f"/ExternalDataConn/ConnKey/{connkey}", headers=headers, verify=VERIFY_HTTPS)
            
            if res.status_code != 200:
                if res.status_code == 404: raise Exception("ExternalDataConnection not found, please check your connkey")
                if res.status_code == 401: raise Exception("Unauthorized")
                if res.status_code == 403: raise Exception("Forbidden: please check your token or access permissions")
                raise Exception(f"Error getting external data connection, {res.status_code} {res.text}")
            
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return ExternalDataConnectionDTO(from_response=True, **content["data"])
        except Exception as e:
            raise e

    """
    Get inputstream by ikey
    params:
        ikey: str -> inputstream key
    """
    def get_inputstream_by_ikey(self, ikey:str) -> Inputstream:
        try:
            headers = { "Authorization": f"A2G {self.token}"}

            res = requests.get(APIGW + f"/Inputstream/Ikey/{ikey}", headers=headers, verify=VERIFY_HTTPS)
            if res.status_code != 200:
                if res.status_code == 404: raise Exception("Inputstream not found, please check your ikey")
                if res.status_code == 401: raise Exception("Unauthorized")
                if res.status_code == 403: raise Exception("Forbidden: please check your token or access permissions")
                raise Exception(f"Error getting inputstream, {res.status_code} {res.text}")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return Inputstream(from_response=True, **content["data"])
        except Exception as e:
            raise e
        

    async def _write_to_file(self, ikey:str, query, data:list[dict]) -> None:
        if not os.path.exists(f".acelerai_cache/")               : os.mkdir(f".acelerai_cache/")
        if not os.path.exists(f".acelerai_cache/data/")          : os.mkdir(f".acelerai_cache/data/")
        if not os.path.exists(f".acelerai_cache/data/{ikey}/")   : os.mkdir(f".acelerai_cache/data/{ikey}/")
        
        query_str = json.dumps(query, cls=CustomJSONEncoder)
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()

        # save data
        file_name = f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"

        # Garantiza que solo una tarea escriba a la vez
        async with self.lock:  
            with open(file_name, "ab") as file:
                for record in data:
                    file.write(packer.pack(record))

    async def fetch_bigpage(self, ikey: str, query: dict, retries_native_is: int = 0, retry_type: TYPE_OF_RETRY = TYPE_OF_RETRY.RETRY_FROM_ERROR) -> None:
        async with SEM:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            my_body = { "query": json.dumps(query, cls=CustomJSONEncoder), "retries": retries_native_is, "retry_type": retry_type.value }

            buffer = b""  # Buffer para ensamblar datos incompletos
            timeout = httpx.Timeout(10800.0, connect=10.0, read=10800.0)
            retries = 0
            backoff = INITIAL_BACKOFF

            while retries < MAX_RETRIES:
                try:
                    logger.info(f"Downloading data on retry {retries}")
                    async with httpx.AsyncClient(http2=True, verify=VERIFY_HTTPS, timeout=timeout) as client:
                        async with client.stream(
                            "POST",
                            f"{QUERY_MANAGER}/QueryData/Find",
                            json=my_body,
                            headers=headers,
                            params={"page": 0, "page_size": 0}
                        ) as response:

                            if response.status_code != 200:
                                msg = ''
                                async for chunk in response.aiter_bytes():
                                    if chunk:
                                        msg += chunk.decode("utf-8")
                                raise Exception(f"{response.status_code} {msg}")

                            rows_count = 0
                            attempt_count = 0  # Contador de reintentos
                            async for chunk in response.aiter_bytes():
                                buffer += chunk  # Agregar los datos al buffer
                                while len(buffer) >= 4:  # Asegurarse de que al menos 4 bytes están disponibles
                                    obj_length = struct.unpack(">I", buffer[:4])[0]

                                    if len(buffer) < 4 + obj_length:
                                        break  # Esperar más datos si el objeto no está completo

                                    obj_data = buffer[4:4 + obj_length]
                                    buffer = buffer[4 + obj_length:]  # Actualizar el buffer
                                    decompressed_data = gzip.decompress(obj_data)  # Descomprimir los datos
                                    data = msgpack.unpackb(decompressed_data, object_hook=decode_datetime)  # Deserializar el objeto
                                    if not isinstance(data, list):
                                        if "acceler_error" in data:
                                            raise Exception(data["message"])    
                                        if "aceler_retry" in data:
                                            logger.info(f"Retrying data download. Retry number {data['retry_count']} of {data['max_retries']}")	
                                            attempt_count += 1
                                        else:
                                            raise Exception("Unexpected data format received, expected a list of dictionaries.")
                                        
                                    if not isinstance(data, list) and "aceler_retry" in data and retry_type == TYPE_OF_RETRY.RETRY_FROM_BEGINNING:           
                                            #eliminar el archivo de cache
                                            query_str = json.dumps(query, cls=CustomJSONEncoder)
                                            query_hash = hashlib.sha256(query_str.encode()).hexdigest()

                                            # vaciar
                                            file_name = f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"
                                            #vaciar archivo
                                            if os.path.exists(file_name):
                                                os.remove(file_name)
                                            rows_count = 0   
                                    if isinstance(data, list):
                                        rows_count += len(data)
                                        if rows_count % 20000 == 0: logger.info(f"Downloaded {rows_count} rows")

                                        # Procesar y guardar los datos
                                        await self._write_to_file(ikey, query, data)
                    logger.info(f"Downloaded data on retry {retries}")
                    logger.info(f"total number of attempts to obtain data: {attempt_count}")
                    break  # Si todo va bien, salimos del bucle
                except (httpx.StreamError, httpx.ConnectError, httpx.ReadTimeout) as e:
                    # Manejar errores específicos de conexión y reinicio
                    retries += 1
                    if retries >= MAX_RETRIES:
                        raise Exception(f"Max retries exceeded: {e}")
                    logger.warning(f"Error: {e}. Retrying in {backoff} seconds...")
                    await asyncio.sleep(backoff)
                    backoff *= BACKOFF_MULTIPLIER  # Incrementar el tiempo de espera exponencialmente

    async def find_one(self, ikey:str, query:dict) -> bool:
        try:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            async with httpx.AsyncClient(verify=VERIFY_HTTPS) as client:
                res = await client.post(f"{QUERY_MANAGER}/QueryData/FindOne", 
                    data=json.dumps(query, cls=CustomJSONEncoder),
                    headers=headers
                )

            if res.status_code != 200:
                raise Exception(f"Error getting inputstream data {res.status_code} {res.content}")
            content = res.json(cls=CustomJsonDecoder)
            await self._write_to_file(ikey, query, [content["data"]])
            return True
            
        except Exception as e:
            raise False


    async def fetch_page_agg(self, client: httpx.AsyncClient, ikey: str, pipeline:list[dict], page, page_size):
        
        logger.info(f"Downloading page {page}")
        async with SEM:
            res = await client.post(
                f"{QUERY_MANAGER}/QueryData/Aggregate",
                params = {"page": page, "page_size": page_size},
                data = json.dumps(pipeline, cls=CustomJSONEncoder)
            )

            logger.info(f"Code Res: {res.status_code}")
            if res.status_code != 200: raise Exception(f"Error getting inputstream data {res.status_code} {res.content}")
            content = res.json(cls=CustomJsonDecoder)
            
            await self._write_to_file(ikey, pipeline, content["data"])
            logger.info(f"Downloaded page {page}")


    async def aggregate(self, ikey:str, pipeline:list[dict]) -> bool:
        try:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            res = requests.post(f"{QUERY_MANAGER}/QueryData/ExecutionPlanningAggregate", 
                data    = json.dumps(pipeline, cls=CustomJSONEncoder), 
                headers = headers, 
                verify  = VERIFY_HTTPS
            )
            if res.status_code != 200: 
                raise Exception(f"Error getting execution planning {res.status_code} {res.content}")
            
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            
            total_docs      = content["data"]["total"]
            page_size       = content["data"]["size"]
            total_batchs    = (total_docs // page_size) + 1
            logger.info(f"Total documents to download {total_docs}, batch size {page_size}, total batchs {total_batchs}")
            if total_docs == 0: return False

            client = httpx.AsyncClient(headers=headers, verify=VERIFY_HTTPS, timeout=httpx.Timeout(60.0, connect=10.0, read=1200.0))
            tasks = []
            for page in range(1, total_batchs + 1):
                tasks.append(self.fetch_page_agg(client, ikey, pipeline, page, page_size))
            await asyncio.gather(*tasks)

            logger.info("All pages downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error to aggregate data in inputstream {e}", stack_info=True)
            return False


    def send_example(self, ikey:str, example:dict) -> dict:
        try:
            headers = { 
                "Authorization": f"A2G {self.token}", 
                "ikey": ikey,
                'Content-Type': 'application/json'
            }
            res = requests.post(f"{DATA_URL}/Data/Insert", 
                data=json.dumps(example, cls=CustomJSONEncoder),
                headers=headers, 
                verify=VERIFY_HTTPS
            )
            if res.status_code != 200: raise Exception(f"Error sending example {res.status_code} {res.content}")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return content["data"]
        except Exception as e:
            raise e
        

    async def insert_data(self, 
        ikey:str, 
        data:list[dict], 
        mode:INSERTION_MODE, 
        wait_response:bool,
        batch_idx:int,
        batch_size:int
    ) -> tuple[int, str]:
        """
        insert data into inputstream internal
        params:
            ikey: str
            data: list[dict]
            mode: INSERTION_MODE
            wait_response: bool
            i: int -> only for logging
            batch_size: int -> only for logging
        """
        try:
            async with SEM:
                timeout = httpx.Timeout(60.0, connect=10.0, read=600.0)
                async with httpx.AsyncClient(verify=VERIFY_HTTPS, timeout=timeout) as client:

                    # TODO: revisar si se puede gzipper el contenido
                    headers = {
                        "Authorization": f"A2G {self.token}",
                        "ikey": ikey,
                        'Content-Type': 'application/json',
                        "Content-Encoding": "gzip"
                    }

                    if mode == INSERTION_MODE.REPLACE: 
                        headers["Replace"] = "true"
                        headers["Transaction"] = "false"

                    elif mode == INSERTION_MODE.INSERT_UNORDERED: 
                        headers["Replace"] = "false"
                        headers["Transaction"] = "false"

                    elif mode == INSERTION_MODE.TRANSACTION:
                        headers["Replace"] = "false"
                        headers["Transaction"] = "true"

                    if wait_response: headers["WaitResponse"] = "true"

                    # Envia un lote de datos al servidor
                    body = gzip.compress(json.dumps(data, cls=CustomJSONEncoder).encode(), compresslevel=7)
                    start = datetime.datetime.now()
                    logger.info(f"Inserting batch {batch_idx} into inputstream {ikey}...")
                    response:Response = await client.post(f"{DATA_URL}/Data/Insert", content = body, headers = headers)
                    if response.status_code != 200: 
                        raise Exception(f"Error to insert data in inputstream {response.status_code} {response.text}")
                    logger.info(f"Batch {batch_idx} received successfully, batch size: {batch_size}, elapsed time: {datetime.datetime.now() - start}")
                    return response.status_code, response.text
                
        except Exception as e:
            logger.error(f"Error to insert data in inputstream {e}", exc_info=True)
            raise e


    def convert_types(self, value):
        try:
            if value is None:
                return None
            elif isinstance(value, (int, float, str, bool)):
                if isinstance(value, float) and math.isnan(value):
                    return None  # Serializar NaN como NULL
                return value
            elif isinstance(value, Decimal):
                if value.is_nan():
                    return None  # Serializar NaN como NULL
                return str(value)
            elif isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                return value.isoformat()
            elif isinstance(value, UUID):
                return str(value)
            elif isinstance(value, bytes):
                return base64.b64encode(value).decode("utf-8")
            else:
                raise Exception(f"Tipo no soportado: {type(value)}")
        except Exception as e:
            raise(e)

    async def data_generator(self, data_source, batch_size, table_name):
        """
        Un generador asíncrono que envía datos en lotes como chunks.
        """
        batch = []
        self.sent_records = 0
        total_records = len(data_source)
        for record in data_source:
            batch.append(record)
            if len(batch) == batch_size:                            
                payload = {
                    "list_data": [{key: self.convert_types(value) for key, value in row.items()} for row in batch],
                    "table_name": table_name,
                }
                logger.info(f"Current status: {self.sent_records} of {total_records} >> sending {len(batch)}")
                self.sent_records += len(batch)
                yield msgpack.packb(payload) + b'>I<I'
                batch = []
        # Procesar los datos restantes si no alcanzaron el tamaño del batch
        if batch:                    
            payload = {
                "list_data": [{key: self.convert_types(value) for key, value in row.items()} for row in batch],
                "table_name": table_name,
            }
            logger.info(f"Current status: {self.sent_records} of {total_records} >> sending {len(batch)}")
            self.sent_records += len(batch)
            yield msgpack.packb(payload) + b'>I<I'

    async def insert_data_big_external(self, conn_key:str, table: str, data:list[dict]) -> None:
        """
        insert big data into external connection using http2 and stream
        params:
            conn_key: str -> connection key
            table_name: str -> table name
            data: list[dict] -> data to insert
        """
        batch_size = 50000
        
        try:            
            timeout = httpx.Timeout(connect=10.0, read=600.0, write=600.0, pool=600.0)
            async with httpx.AsyncClient(http2=True, verify=VERIFY_HTTPS, timeout=timeout) as client:
                # TODO: revisar si se puede gzipper el contenido
                headers = {
                    "Authorization": f"A2G {self.token}",
                    "ikey": conn_key,
                    'Content-Type': 'text/plain'
                }
                logger.info(f"Inserting data into external connection {conn_key}...")
                async with client.stream("POST",f"{QUERY_MANAGER}/QueryData/InsertDataBigExternal",
                    content = self.data_generator(data, batch_size=batch_size, table_name=table), 
                    headers = headers
                ) as response:              
                    if response.status_code == 200:
                        async for line in response.aiter_text():  # Procesar línea por línea
                            logger.info(f"Server response: {line}")
                            res_json = json.loads(line)                            
                            return res_json['success']
                    else:
                        await response.aread()  # Leer el contenido para evitar bloqueos
                        if response.status_code == 403:
                            logger.error(f"Forbidden: please check your token or access permissions in the resource") 
                            return False   
                        if response.status_code == 500:
                            logger.error(f"Internal server error: {response.text}")
                            return False
                        if response.status_code == 404:
                            logger.error(f"External data connection not found, please check your connection key")
                            return False
                        else:
                            logger.error(f"Failed to insert data: {response.status_code} - {response.text}")
                            return False
        except asyncio.CancelledError as e:
            logger.info(f"La tarea fue cancelada: {e}")
            return False
        
        except Exception as e:
            logger.info(f"Error general: {e}")     
            logger.info(f"Error general: {repr(e), {traceback.format_exc()}}")  
            return False
        return True


    async def remove_documents(self, ikey: str, query: dict) -> int:
        try:
            logger.info("Removing data...")
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            if len(query) == 0: 
                raise Exception("Query is empty, please provide a valid query. If you desire to delete all documents, use the clear_inputstream method.")

            async with httpx.AsyncClient(verify=VERIFY_HTTPS) as client:
                response = await client.post(
                    f"{QUERY_MANAGER}/QueryData/RemoveDocuments",
                    data=json.dumps(query, cls=CustomJSONEncoder),
                    headers=headers,
                    timeout = httpx.Timeout(60.0, connect=10.0, read=600.0)
                )

            if response.status_code != 200: 
                raise Exception(f"Error to remove data in inputstream {response.status_code} {response.content}")
            
            res_object = json.loads(response.text, cls=CustomJsonDecoder)
            if not res_object["success"]: 
                raise Exception(res_object["errorMessage"])

            content = res_object["data"]
            deleted_docs = content["docs_affected"]
            logger.info(f"Operation complete, total docs deleted: {deleted_docs}")

            return deleted_docs
        except Exception as e:
            raise e


    async def clear_inputstream(self, ikey:str) -> int:
        try:
            logger.info("Removing all data...")
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey
            }

            async with httpx.AsyncClient(verify=VERIFY_HTTPS) as client:
                response = await client.post(
                    f"{QUERY_MANAGER}/QueryData/Clear",
                    headers=headers,
                    timeout = httpx.Timeout(60.0, connect=10.0, read=600.0)
                )

            if response.status_code != 200:
                raise Exception(f"Error to remove all data in inputstream {response.status_code} {response.content}")
            
            res_object = response.json(cls=CustomJsonDecoder)
            if not res_object["success"]: raise Exception(res_object["errorMessage"])
            
            content = res_object["data"]
            deleted_docs = content["docs_affected"]
            logger.info(f"Operation complete, total docs deleted: {deleted_docs}")
            return deleted_docs
        except Exception as e:
            logger.error(f"Error to clear inputstream {e}", exc_info=True)
            raise e
        


    ##############################################################
    
    def upload_asset(self, pkey:str, local_file_path:str, storage_path:str) -> Asset:
        """
        Upload file to the asset storage
        Please note: if your connection is to MongoDB, the query must be as follows: {"collection_name":"your_collection", "query":'{your_query}'}
        params:
            conn_key: str
            query: dict | str
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        headers = { "Authorization": f"A2G {self.token}"}
        
        file_stream = open(local_file_path, 'rb')
        files = {'file': (f'{local_file_path.split("/")[-1]}', file_stream)}
        
        endpoint = f"{APIGW}/Project/{pkey}/Assets/Upload"
        response = requests.post(endpoint, data = {'path': storage_path}, files = files, headers=headers, verify=VERIFY_HTTPS)
        content = response.json(cls=CustomJsonDecoder)
        if response.status_code == 200:
            logger.info(f"Asset replaced successfully")
            if not content["success"]: raise Exception(content["errorMessage"])
            asset_data = content["data"]
            return Asset(
                id=asset_data["id"],
                path=asset_data["path"],
                created_at=asset_data["createdAt"],
                url=asset_data["url"],
                size=asset_data["size"]
            )
        elif response.status_code == 201:
            logger.info(f"Asset created successfully")
            if not content["success"]: raise Exception(content["errorMessage"])
            asset_data = content["data"]
            return Asset(
                id=asset_data["id"],
                path=asset_data["path"],
                created_at=asset_data["createdAt"],
                url=asset_data["url"],
                size=asset_data["size"]
            )
        else:
            logger.error(f"Request failed with status code {response.status_code}")
            raise Exception(f"Error uploading asset {response.status_code} {response.text}")


    def get_asset_by_id(self, uid:str) -> Asset:
        """
        Get asset by its unique id
        params:
            uid: str -> unique identifier of the asset
        """
        headers = {"Authorization": f"A2G {self.token}"}
        endpoint = f"{APIGW}/Assets/{uid}"
        response = requests.get(endpoint, headers=headers, verify=VERIFY_HTTPS)
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}")
            raise Exception(f"Error getting asset {response.status_code} {response.text}")
        content = response.json(cls=CustomJsonDecoder)
        if not content["success"]:
            raise Exception(content["errorMessage"])
        asset_data = content["data"]
        return Asset(
            id=asset_data["id"],
            path=asset_data["path"],
            created_at=asset_data["createdAt"],
            url=asset_data["url"],
            size=asset_data["size"]
        )


    def get_asset_by_path(self, pkey:str, path:str) -> Asset:
        """
        Get asset by project key and path
        params:
            pkey: str -> project key
            path: str -> path of the asset
        """
        headers = {"Authorization": f"A2G {self.token}"}
        endpoint = f"{APIGW}/Project/{pkey}/Assets/{path}"
        response = requests.get(endpoint, headers=headers, verify=VERIFY_HTTPS)
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}")
            raise Exception(f"Error getting asset by path {response.status_code} {response.text}")
        content = response.json(cls=CustomJsonDecoder)
        if not content["success"]:
            raise Exception(content["errorMessage"])
        asset_data = content["data"]
        return Asset(
            id=asset_data["id"],
            path=asset_data["path"],
            created_at=asset_data["createdAt"],
            url=asset_data["url"],
            size=asset_data["size"]
        )


    def download_userfile(self, url:str, save_path:str):
        """
        Download a file from a given URL and save it to the specified path using streaming.
        :param url: The URL of the file to download.
        :param save_path: The local path where the file will be saved.
        """
        headers = {"Authorization": f"A2G {self.token}"}
        with requests.get(url, headers=headers, verify=VERIFY_HTTPS, stream=True) as r:
            r.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size = 1024*1024):  # 1 MB chunks
                    if chunk:
                        f.write(chunk)
        logger.info(f"File downloaded successfully to {save_path}")
    

    def list_assets(self, pkey:str, page:int=1, page_size:int=100, folder_path:str = None, text_search:str = None) -> PaginationData[Asset]:
        """
        List assets in a project with pagination and optional filters.
        params:
            pkey: str -> project key
            page: int -> page number (default is 1)
            page_size: int -> number of items per page (default is 100)
            folder_path: str -> optional folder path to filter assets
            text_search: str -> optional text search to filter assets
        """
        headers = { "Authorization": f"A2G {self.token}", }

        params = { "page": page, "pageSize": page_size }
        if folder_path is not None: params["folderPath"] = folder_path
        if text_search is not None: params["textSearch"] = text_search
        endpoint = f"{APIGW}/Project/{pkey}/Assets"
        response = requests.get(endpoint, headers=headers, verify=VERIFY_HTTPS, params=params)
        api_response = response.json(cls=CustomJsonDecoder)

        if response.status_code == 200:
            assets_list = api_response['data']['data']
            total = api_response['data']['total']

            assets:list[Asset] = []
            for asset in assets_list:
                asset = Asset(
                    id=asset['id'],
                    path=asset['path'],
                    created_at=asset['createdAt'],
                    url=asset['url'],
                    size=asset['size']
                )
                assets.append(asset)

            page_data = PaginationData(
                data=assets,
                total_items=total,
                page=page,
                page_size=page_size
            )

            return page_data
        else:
            logger.error(f"Request failed with status code {response.status_code}")

        return response.json()


    def delete_asset_by_id(self, asset_id:str) -> bool:
        """
        Delete an asset by its unique id.
        params:
            asset_id: str -> unique identifier of the asset
        """
        headers = {"Authorization": f"A2G {self.token}"}
        endpoint = f"{APIGW}/Assets/{asset_id}"
        response = requests.delete(endpoint, headers=headers, verify=VERIFY_HTTPS)
        
        if response.status_code == 200:
            logger.info(f"Asset {asset_id} deleted successfully.")
            return True
        else:
            logger.error(f"Failed to delete asset {asset_id}: {response.status_code} {response.text}")
            return False
        

    def delete_asset_by_path(self, pkey:str, path:str) -> bool:
        """
        Delete an asset by project key and path.
        params:
            pkey: str -> project key
            path: str -> path of the asset
        """
        headers = {"Authorization": f"A2G {self.token}"}
        endpoint = f"{APIGW}/Project/{pkey}/Assets/{path}"
        response = requests.delete(endpoint, headers=headers, verify=VERIFY_HTTPS)
        content = response.json(cls=CustomJsonDecoder)
        if response.status_code == 200:
            logger.info(f"Asset at path {path} in project {pkey} deleted successfully.")
            return True
        else:
            logger.error(f"Failed to delete asset at path {path} in project {pkey}: {response.status_code} {response.text}")
            return False


    def download_folder(self, pkey:str, folder_path:str, save_path:str):
        """
        Download all assets in a folder to a local path.
        params:
            pkey: str -> project key
            folder_path: str -> path of the folder in the project
            local_path: str -> local path where the assets will be downloaded
        """
        
        # get folders
        dirs = save_path.split('/')
        if len(dirs) > 1:
            local_folder_path = '/'.join(dirs[:-1])
            if not os.path.exists(local_folder_path):
                os.makedirs(local_folder_path)

        headers = {"Authorization": f"A2G {self.token}"}
        endpoint = f"{APIGW}/Project/{pkey}/Assets/Folder/{folder_path}"
        with requests.get(endpoint, headers=headers, verify=VERIFY_HTTPS, stream=True) as r:
            r.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size = 1024*1024):  # 1 MB chunks
                    if chunk:
                        f.write(chunk)
        logger.info(f"File downloaded successfully to {save_path}")