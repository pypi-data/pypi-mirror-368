import os
import asyncio
from  acelerai_inputstream import InputstreamClient

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

async def main():
    client = InputstreamClient(token='7fd3640954424cba8518309e11939027')
    test = await client.find("e5803b1c08364d7c8b37", {})
    print(len(test))
    print(test[0])

if __name__ == '__main__':
    asyncio.run(main())