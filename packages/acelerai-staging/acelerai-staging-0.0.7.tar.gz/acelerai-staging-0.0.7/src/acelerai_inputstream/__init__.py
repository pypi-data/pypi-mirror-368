import json
import os
import logging
logger = logging.getLogger(__name__)

__mode = os.environ.get("EXEC_LOCATION", "LOCAL")
logger.info(f"EXEC_LOCATION: {__mode}")
if __mode == "LOCAL":
    # Environment production
    DATA_URL        = os.environ.get("DATA_URL"         , "https://stream.aceler.ai")
    QUERY_MANAGER   = os.environ.get("QUERY_MANAGER"    , "https://stream.aceler.ai")  
    APIGW           = os.environ.get("APIGW"            , "https://apigw.aceler.ai")
    VERIFY_HTTPS    = os.environ.get("VERIFY_HTTPS", "true").lower().strip() == "true"

elif __mode == "PRODUCTION":
    # Environment production
    DATA_URL        = os.environ.get("DATA_URL"         , "https://inputstreamdata-service.aceler-ai.svc.cluster.local:1008")
    QUERY_MANAGER   = os.environ.get("QUERY_MANAGER"    , "https://querymanager-service.aceler-ai.svc.cluster.local:1012")
    APIGW           = os.environ.get("APIGW"            , "https://apigateway-service.aceler-ai.svc.cluster.local:1000")
    VERIFY_HTTPS = False

else:
    raise Exception(f"Invalid environment {__mode}, please check the EXEC_LOCATION environment variable")


from acelerai_inputstream.models.inputstream import INSERTION_MODE, Inputstream
from acelerai_inputstream.inputstream_client import InputstreamClient

__mode = os.environ.get("EXEC_LOCATION", "LOCAL")