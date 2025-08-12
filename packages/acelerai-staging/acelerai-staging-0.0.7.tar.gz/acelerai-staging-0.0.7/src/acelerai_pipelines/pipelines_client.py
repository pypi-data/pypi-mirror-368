import logging
import time
from typing import Coroutine
from uuid import UUID

from acelerai_pipelines.http_aceler_pipelines import AcelerAIHttpPipelinesClient
from acelerai_pipelines.models.run import Run, RunStatus
from acelerai_pipelines.models.pagination_data import PaginationData
logger = logging.getLogger("InputstreamClient")

import os


class PipelinesClient:
    """
    Client to interact with ACELER.AI inputstreams
    """

    def __init__(self, token:str):
        """
        Constructor for LocalInputstream
        :param token: Token to authenticate with ACELER.AI
        :param cache_options: { duration_data: int, duration_inputstream: int } | None
        """        
        self.acelerai_client = AcelerAIHttpPipelinesClient(token)
        self.__mode = os.environ.get("EXEC_LOCATION", "LOCAL")


    async def execute_run_ondemand(self, deploy_key: str, payload:dict|None = None) -> Run:
        """
        Execute a run on demand
        :param deploy_id: The deploy id to be executed
        :param payload: The payload to be used in the run
        :return: The run object
        """
        logger.info(f"Executing run on demand - Deploy ID: {deploy_key}")

        deploy = await self.acelerai_client.get_deploy_by_fkey(deploy_key)
        if deploy is None:
            raise Exception(f"Deploy {deploy_key} not found in your account, please check the deploy key or your credentials")

        if deploy.DeployInfo.Actived == False:
            raise Exception(f"Deploy {deploy_key} is not active, please activate the deploy in pipelines dashboard")

        run = await self.acelerai_client.execute_run_ondemand(deploy_key, payload)
        if run is None:
            raise Exception(f"Error executing run on demand - Deploy ID: {deploy_key}")
        return run
    

    async def get_run(self, run_id: UUID | str, wait_result = True) -> Run:
        """
        Get the result of a run
        :param run_id: The run id
        :return: The run object
        """
        run_id = str(run_id)
        logger.info(f"Getting run result - Run ID: {run_id}")

        while True:
            run = await self.acelerai_client.get_run(run_id)
            if not wait_result: return run

            if run.RunStatus == RunStatus.Error:
                logger.error(f"Error in run - Run ID: {run_id}")
                return run
            
            if run.RunStatus == RunStatus.Completed:
                logger.info(f"Run completed - Run ID: {run_id}")
                return run
            
            if run.RunStatus == RunStatus.Cancelled:
                logger.error(f"Run was cancelled - Run ID: {run_id}")
                return run
            
            if run.RunStatus == RunStatus.InternalError:
                logger.error(f"Internal error in run, please communicate with support - Run ID: {run_id}")
                return run
            
            if run.RunStatus == RunStatus.Lost:
                logger.error(f"Run was lost - Run ID: {run_id}")
                return run
            
            if run.RunStatus == RunStatus.Pending:
                logger.info(f"Run is pending - Run ID: {run_id}")
            
            if run.RunStatus == RunStatus.Running:
                logger.info(f"Run is running - Run ID: {run_id}")
            
            time.sleep(3)


    async def get_deploy_runs(self, deploy_key:str, page = 1, page_size = 10) -> PaginationData[Run]:
        """
        Get runs
        :param deploy_key: The deploy key
        :param page: The page number
        :param page_size: The page size
        :return: The list of runs
        """
        logger.info(f"Getting runs - Deploy Key: {deploy_key}")
        data_page = await self.acelerai_client.get_deploy_runs(deploy_key, page, page_size)
        return data_page



