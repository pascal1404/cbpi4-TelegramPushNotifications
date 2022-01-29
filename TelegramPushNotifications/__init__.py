
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
from telethon import *
import re
import random
import cbpi
from .callbacks import TelegramCallbacks
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
import requests
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationType
from cbpi.controller.notification_controller import NotificationController
from cbpi.http_endpoints.http_notification import NotificationHttpEndpoints

logger = logging.getLogger(__name__)

telegram_bot_token = None
telegram_chat_id = None
telegram = None
telegram_api_id = None
telegram_api_hash = None
bot = None

class Telegram(CBPiExtension):

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self.controller : StepController = cbpi.step
        self.cbpi.register(self, "/step2")
        self.cbpi.bus.register_object(self)
        self._task = asyncio.create_task(self.run())
        

    # async def set_commands(self):
        # cmd_list = [
        # {"command":"help","description":"get a list of all commands with description"},
        # {"command":"next","description":"Next Brew Step"},
        # {"command":"start","description":"start brewing"},
        # {"command":"stop","description":"stop brewing"},
        # {"command":"set_target","description":"set Target Temperature of the item you choose"},
        # {"command":"get_target","description":"get Target Temperature of all items"},
        # {"command":"get_timer","description":"get the actual countdown time"},
        # {"command":"get_chart","description":"send Picture of chart from the item you choose"},
        # {"command":"get_parameter","description":"get all parameters of the item you choose"}]
        # if telegram_bot_token is not None and telegram_chat_id is not None:
            # url = "https://api.telegram.org/bot" + telegram_bot_token + "/setMyCommands"
            # escapedUrl = requests.Request('GET', url,
                                        # params={"chat_id": telegram_chat_id,
                                                # "commands": json.dumps(cmd_list)}
                                        # ).prepare().url
            # requests.get(escapedUrl)
                
    async def run(self):
        global bot
        logger.info('Starting TelegramPushNotifications background task')
        await self.telegramChatId()
        await self.telegramBotToken()
        await self.telegramAPIId()
        await self.telegramAPIHash()
        if telegram_bot_token is None or telegram_bot_token == "" or not telegram_bot_token:
            logger.warning('Check Telegram Bot API Token is set')
        elif telegram_chat_id is None or telegram_chat_id == "" or not telegram_chat_id:
            logger.warning('Check Telegram Chat ID is set') 
        elif telegram_api_id is None or telegram_api_id == "" or not telegram_api_id:
            logger.warning('Check Telegram API Id is set')
        elif telegram_api_hash is None or telegram_api_hash == "" or not telegram_api_hash:
            logger.warning('Check Telegram API Hash is set')
        else:
            self.listener_ID = self.cbpi.notification.add_listener(self.messageEvent)
            logger.info("Telegram Bot Listener ID: {}".format(self.listener_ID))
            ############################## Nur zum Testen wie ich an die Daten komme
            kettles = self.cbpi.kettle.get_state()
            fermenter = self.cbpi.fermenter.get_state()
            actors = self.cbpi.actor.get_state()
            sensors = self.cbpi.sensor.get_state()
            logger.warning(kettles)
            logger.info(" ")
            await self.controller.start()
            logger.warning(fermenter)
            logger.info(" ")
            logger.warning(actors)
            logger.info(" ")
            logger.warning(sensors)
            logger.info(" ")
            steps = self.cbpi.step.get_state()
            for value in steps["steps"]:
                step = self.cbpi.step.find_by_id(value["id"])
                logger.warning("{}".format(value))
                logger.warning("{}".format(step.instance.summary))
                logger.warning("{}".format(value["state_text"]))
            buttons = []
            for value in kettles["data"]:
                logger.info(value["name"])
                # logger.warning(self.cbpi.sensor.get_sensor_value(value["id"])["value"])
                # buttons.append(Button.inline(value["name"],value["id"]))
            for value in fermenter["data"]:
                logger.info(value["name"])
                # buttons.append(Button.inline(value["name"],value["id"]))

            # await self.controller.stop()
            # steps = self.cbpi.step.get_state()
            # for value in steps["steps"]:
                # logger.warning("{}: {}".format(value["name"],value["status"]))
                
            # await self.controller.next()
            # steps = self.cbpi.step.get_state()
            # for value in steps["steps"]:
                # logger.warning("{}: {}".format(value["name"],value["status"]))
                
            # await self.controller.stop()
            # steps = self.cbpi.step.get_state()
            # for value in steps["steps"]:
                # logger.warning("{}: {}".format(value["name"],value["status"]))
                
                
            # await self.controller.start()
            # steps = self.cbpi.step.get_state()
            # for value in steps["steps"]:
                # logger.warning("{}: {}".format(value["name"],value["status"]))
                
            ######################################################## ende Testdaten
            bot = await TelegramClient('bot', int(telegram_api_id), telegram_api_hash).start(bot_token=telegram_bot_token)
            # await bot.send_message(int(telegram_chat_id), "**Hello**\n__I'm your **new** bot!__")
            bot.add_event_handler(callbacks.TelegramCallbacks.callbackQuery)
            bot.add_event_handler(callbacks.TelegramCallbacks.help)
            bot.add_event_handler(callbacks.TelegramCallbacks.next)
            bot.add_event_handler(callbacks.TelegramCallbacks.start)
            bot.add_event_handler(callbacks.TelegramCallbacks.stop)
            bot.add_event_handler(callbacks.TelegramCallbacks.setTarget)
            bot.add_event_handler(callbacks.TelegramCallbacks.getTarget)
            bot.add_event_handler(callbacks.TelegramCallbacks.getTimer)
            bot.add_event_handler(callbacks.TelegramCallbacks.new_message_handler)
            logger.warning("ende")

    async def telegramBotToken(self):
        global telegram_bot_token
        telegram_bot_token = self.cbpi.config.get("telegram_bot_token", None)
        if telegram_bot_token is None:
            logger.info("INIT Telegram Bot Token")
            try:
                await self.cbpi.config.add("telegram_bot_token", "", ConfigType.STRING, "Telegram Bot Token")
            except:
                logger.warning('Unable to update config')

    async def telegramAPIId(self):
        global telegram_api_id
        telegram_api_id = self.cbpi.config.get("telegram_api_id", None)
        if telegram_api_id is None:
            logger.info("INIT telegram API Id")
            try:
                await self.cbpi.config.add("telegram_api_id", "", ConfigType.STRING, "Telegram API Id")
            except:
                logger.warning('Unable to update config')

    async def telegramAPIHash(self):
        global telegram_api_hash
        telegram_api_hash = self.cbpi.config.get("telegram_api_hash", None)
        if telegram_api_hash is None:
            logger.info("INIT telegram API Hash")
            try:
                await self.cbpi.config.add("telegram_api_hash", "", ConfigType.STRING, "Telegram API Hash")
            except:
                logger.warning('Unable to update config')

    async def telegramBotToken(self):
        global telegram_bot_token
        telegram_bot_token = self.cbpi.config.get("telegram_bot_token", None)
        if telegram_bot_token is None:
            logger.info("INIT Telegram Bot Token")
            try:
                await self.cbpi.config.add("telegram_bot_token", "", ConfigType.STRING, "Telegram Bot Token")
            except:
                logger.warning('Unable to update config')

    async def telegramChatId(self):
        global telegram_chat_id
        telegram_chat_id = self.cbpi.config.get("telegram_chat_id", None)
        if telegram_chat_id is None:
            logger.info("INIT Telegram Chat ID")
            try:
                await self.cbpi.config.add("telegram_chat_id", "", ConfigType.STRING, "Telegram Chat ID")
            except:
                logger.warning('Unable to update config')

    async def messageEvent(self, cbpi, title, message, type, action):
        
        if telegram_bot_token is not None and telegram_chat_id is not None:
            temp = 0
            await bot.send_message(int(telegram_chat_id), "**{}**\n__{}__".format(title,message))

def setup(cbpi):
    cbpi.plugin.register("TelegramPushNotifications", Telegram)
    pass

