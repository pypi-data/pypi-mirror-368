import asyncio
import json
import httpx
import msgpack
from acelerai_pipelines import APIGW, VERIFY_HTTPS
from acelerai_pipelines.models.deploy import Deploy
from acelerai_pipelines.models.run import Run
from acelerai_inputstream.utils import CustomJSONEncoder, CustomJsonDecoder, custom_encoder

# Type conversion

import logging

from acelerai_pipelines.models.pagination_data import PaginationData
logger = logging.getLogger("HttpAcelerAI")

SEM = asyncio.Semaphore(20)  # Limitar concurrencia a 20 conexiones
MAX_RETRIES = 5  # Número máximo de reintentos
INITIAL_BACKOFF = 1  # Tiempo inicial de espera en segundos
BACKOFF_MULTIPLIER = 2  # Factor multiplicador para el tiempo de espera

packer = msgpack.Packer(default=custom_encoder) 


class AcelerAIHttpPipelinesClient():

    def __init__(self, token:str):
        self.token = token

    
    def get_headers(self) -> dict:
        """
        Get the headers for the request
        :return: The headers
        """
        return {
            "Authorization": f"A2G {self.token}",
            "Content-Type": "application/json"
        }


    async def get_deploy_by_fkey(self, fkey:str) -> Deploy | None:
        """
        Get deploy by fkey
        :param fkey: The fkey of the deploy
        :return: The deploy object
        """
        try:
            async with httpx.AsyncClient(verify=VERIFY_HTTPS, timeout = httpx.Timeout(10800.0, connect=10.0, read=10800.0)) as client:
                response = await client.get(f"{APIGW}/Deploy/Fkey/{fkey}", headers=self.get_headers())
                logger.info(f"response {response.status_code} - {response.text}")
                if response.status_code == 200:
                    resp_json = response.json(cls=CustomJsonDecoder)
                    data = resp_json["data"]
                    deploy = Deploy(**data)
                    return deploy
                else:
                    logger.error(f"Error getting deploy by fkey: {fkey}")
                    return None
        except Exception as e:
            logger.error(f"Error getting deploy by fkey: {fkey}", exc_info=True)
            return None
            

    async def execute_run_ondemand(self, deploy_key: str, payload:dict|None = None) -> Run | None:
        """
        Execute a run on demand
        :param deploy_key: The deploy id to be executed
        :param payload: The payload to be used in the run
        :return: The run object
        """
        try:
            body = {
                "fKey": deploy_key,
                "payload": json.dumps(payload, cls=CustomJSONEncoder) if payload is not None else None
            }
            async with httpx.AsyncClient(verify=VERIFY_HTTPS, timeout = httpx.Timeout(10800.0, connect=10.0, read=10800.0)) as client:
                response = await client.post(f"{APIGW}/Run/ExecuteOnDemand", headers=self.get_headers(), json=body)
                if response.status_code == 201: 
                    json_res = response.json(cls=CustomJsonDecoder)
                    data = json_res["data"]
                    run = Run(**data)
                    return run
                else:
                    logger.error(f"Error executing run on demand, {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error executing run on demand - Deploy ID: {deploy_key}", exc_info=True)
            return None
    
    
    async def get_run(self, run_id: str) -> Run | None:
        """
        Get the result of a run
        :param run_id: The run id
        :return: The run object
        """
        try:
            async with httpx.AsyncClient(verify=VERIFY_HTTPS, timeout = httpx.Timeout(10800.0, connect=10.0, read=10800.0)) as client:
                response = await client.get(f"{APIGW}/Run/{run_id}", headers=self.get_headers())
                if response.status_code == 200: 
                    data = response.json()
                    run = Run(**data["data"])
                    return run
                else:
                    logger.error(f"Error getting run - Run ID: {run_id} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error getting run - Run ID: {run_id}", exc_info=True)
            return None
    
    
    async def get_deploy_runs(self, deploy_key:str, page = 1, page_size = 10) -> PaginationData[Run] | None:
        """
        Get runs
        :param deploy_key: The deploy key
        :return: The list of runs
        """
        try:
            async with httpx.AsyncClient(verify=VERIFY_HTTPS, timeout = httpx.Timeout(10800.0, connect=10.0, read=10800.0)) as client:
                response = await client.get(f"{APIGW}/Deploy/{deploy_key}/Run/History?Page={page}&PageSize={page_size}", headers=self.get_headers())
                if response.status_code == 200:
                    data = response.json()
                    runs = [Run(**run) for run in data["data"]["data"]]
                    total = data["data"]["total"]
                    return PaginationData(runs, page, page_size, total)
                elif response.status_code == 400:
                    logger.error(f"Error getting runs - Deploy Key: {deploy_key} - {response.text}")
                elif response.status_code == 404:
                    logger.error(f"Deploy {deploy_key} not found in your account, please check the deploy key or your credentials")
                return None
        
        except Exception as e:
            logger.error(f"Error getting runs - Deploy Key: {deploy_key}", exc_info=True)
            return None