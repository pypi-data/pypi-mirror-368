from acelerai_inputstream import InputstreamClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

#Para desactivar los logs de la librería
#logging.getLogger('InputstreamClient').disabled = True
client = InputstreamClient(token='7ffba0a8bccb4498be8a811b43bd9400') 
input_cycle=client.find(ikey='31feaa0361b44ebb8b70', query= {}, cache=False)



