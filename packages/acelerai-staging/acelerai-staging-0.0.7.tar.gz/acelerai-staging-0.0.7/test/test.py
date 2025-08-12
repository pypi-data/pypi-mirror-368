import os
# os.environ["DATA_URL"]          =  "https://localhost:1008"
# os.environ["QUERY_MANAGER"]     =  "http://localhost:1012"
# os.environ["INPUTSTREAM_URL"]   =  "https://localhost:1000"

from  acelerai_inputstream import InputstreamClient
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

#Para desactivar los logs de la librería
logging.getLogger('InputstreamClient').disabled = False

#pat_danilo='324738f335354e9d80394c31ce1d644c'
client = InputstreamClient(token='084a45f10e3b4952a4f3a7df04f546e5') 

input_cycle=client.find(ikey='74c337b0e99a45ac8a9c', query= {}, cache=False)
df=pd.DataFrame(input_cycle)
#print(len(df))