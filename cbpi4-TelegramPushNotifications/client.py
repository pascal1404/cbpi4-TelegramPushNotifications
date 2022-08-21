from telethon import TelegramClient, events
import aiohttp
import json
import logging

logger = logging.getLogger(__name__)

class Client(TelegramClient):

    def __init__(self, cbpi, session_user_id, api_id, api_hash):
        super().__init__(session_user_id, api_id, api_hash)
        self.cbpi = cbpi

    async def get_items(self, name):
        port = str(self.cbpi.config.get('port', 8000))
        url = "http://localhost:"+port+"/"+name
        logger.info("get_items:{}".format(url))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                res = await response.text()
                return json.loads(res)

    async def post_items(self,  name, postdata):
        port = str(self.cbpi.config.get('port', 8000))
        url = "http://localhost:"+port+"/"+name
        logger.info("post_items:{}".format(url))
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=postdata, headers={"Content-Type": 'application/json', 'User-Agent': "TelegramPlugin"}) as response:
                return await response.text()
