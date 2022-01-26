
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
                
                ########################## Ende der datengenerierung
            logger.warning(telegram_chat_id)
            loop = asyncio.get_running_loop()
            loop.set_debug(True)
            logger.warning(loop)
            
            new_loop = asyncio.new_event_loop()
            # bot = new_loop.run_in_executor(None, test)
            # bot = asyncio.run_coroutine_threadsafe(TelegramClient('bot2', api_id2, api_hash2).start(bot_token=telegram_bot_token2),new_loop)
            # bot = new_loop.call_soon(await TelegramClient('bot2', api_id2, api_hash2).start(bot_token=telegram_bot_token2))
            api_id2 = 123456789
            api_hash2 = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
            telegram_chat_id2 = 987654321
            telegram_bot_token2 = 'xxxxxxxxxxxxxxxxxxxxxxx'
            logger.warning(telegram_chat_id2)
            bot = await TelegramClient('bot2', api_id2, api_hash2).start(bot_token=telegram_bot_token2)
            logger.info("#######################")
            logger.info(bot)
            logger.info("#######################")
            new_loop.run_in_executor(None, await bot.send_message(telegram_chat_id, "**Hello**\n__I'm your **new** bot!__"))
            logger.warning(telegram_chat_id2)

            # try:
                # logger.info(TelegramClient('bot2', api_id2, api_hash2).start(bot_token=telegram_bot_token2))
            # except errors as e:
                # logger.error(e)
            # await bot.start()
            logger.warning(telegram_chat_id)
            # bot.send_message(int(telegram_chat_id), 'Hello, myself!')
            logger.warning(telegram_chat_id)
            # async def main():
                # try:
                    # await bot.send_message(telegram_chat_id, "**Hello**\__I'm your bot!__")
                # except errors.ChatIdInvalidError as e:
                    # logger.warning(e)
                # logger.warning(telegram_chat_id)
                # me = await bot.get_me()
                # logger.warning(me)

                # await bot.loop.run_until_complete(main())
            # with client:
                # client.loop.run_until_complete(main())
            # bot = await TelegramClient('anon', int(telegram_api_id), telegram_api_hash).start(bot_token=telegram_bot_token)
            # logger.warning(int(telegram_chat_id))
            # await bot.send_message('me', 'Hello, myself!')
            # logger.warning(telegram_chat_id)
            # me = bot.get_me()
            # logger.warning(me)
            # Print all dialog IDs and the title, nicely formatted
            # async for dialog in bot.iter_dialogs():
                # logger.warning('{:>14}: {}'.format(dialog.id, dialog.title))
            # logger.warning(await utils.get_peer_id(types.PeerChannel(telegram_chat_id)))
            # await bot.send_message(telegram_chat_id, "**test** \{}".format(steps))

            logger.warning(sensors)
            @bot.on(events.CallbackQuery)
            async def callback(event):
                message = await event.get_message()
                if "get_target_temp" in message:
                    for item in fermenter:
                        if item["id"] == event.data:
                            await event.edit("Target_temp of {} is {].".format(item["name"],self.get_fermenter_target_temp(item["id"])))
                    for item in kettles:
                        if item["id"] == event.data:
                            await event.edit("Target_temp of {} {].".format(item["name"],self.get_kettle_target_temp(item["id"])))
                elif "set_target_temp" in message:
                    for item in fermenter:
                        if item["id"] == event.data:
                            await event.edit("Enter the new target temperature for {}:".format(item["name"]))
                    for item in kettles:
                        if item["id"] == event.data:
                            await event.edit("Enter the new target temperature for {}:".format(item["name"]))
            
            @bot.on(events.NewMessage(pattern='/next'))
            async def next(event):
                await self.controller.next()
                raise events.Stoppropagation
            
            @bot.on(events.NewMessage(pattern='/start'))
            async def start(event):
                await self.controller.start()
                raise events.Stoppropagation
            
            @bot.on(events.NewMessage(pattern='/stop'))
            async def stop(event):
                await self.controller.stop()
                raise events.Stoppropagation
            
            @bot.on(events.NewMessage(pattern='/set_target'))
            async def setTarget(event):
                await bot.send_message(telegram_chat_id, "**Choose Item for set_target_temp**",buttons=buttons)
                raise events.Stoppropagation
            
            @bot.on(events.NewMessage(pattern='/get_target'))
            async def getTarget(event):
                await bot.send_message(telegram_chat_id, "**Choose Item for get_target_temp**",buttons=buttons)
                raise events.Stoppropagation
            
            @bot.on(events.NewMessage(pattern='/get_timer'))
            async def getTimer(event):
                steps = self.cbpi.step.get_state()
                for value in steps["steps"]:
                    if value["status"] == "A":
                        await bot.send_message(telegram_chat_id, "timer of step '{}' is {}.".format(value["name"],value["state_text"]))
                    logger.warning("{}: {}".format(value["name"],value["status"]))
                
                raise events.Stoppropagation
            
            @bot.on(events.NewMessage)
            async def new_message_handler(event):
                async for message in bot.iter_messages(telegram_chat_id,limit=2):
                    if "new target temperature" in message:
                        temp = '999'
                        unit = "°C"
                        match = re.match(r'^(?=(.|,))([+-]?([0-9]*)(\(.|,)([0-9]+))?)$', event.raw_text)
                        number = match.group(1)
                        if number is not None:
                            if 'F' in self.cbpi.config.get("TEMP_UNIT", "C"):
                                unit = "°F"
                                temp = round(9.0 / 5.0 * float(number) + 32, 2)
                            else:
                                temp = float(number)
                            # await self.controller.set_target_temp(id,temp)
                            for item in fermenter:
                                if item["name"] in message:
                                    await self.set_fermenter_target_temp(item["id"],temp)
                                    await bot.send_message(telegram_chat_id, "Set Target_temp of {} to {}{}.".format(item["name"],temp,unit))
                            for item in kettles:
                                if item["id"] in message:
                                    await self.set_target_temp(item["id"],temp)
                                    await bot.send_message(telegram_chat_id, "Set Target_temp of {} to {}{}.".format(item["name"],temp,unit))
                        else:
                            await bot.send_message(telegram_chat_id, "**No valid Input for Set Target_temp of {} found!**".format(item["name"]))

                    if "original gravity" in message:
                        match = re.match(r'^(?=(.|,))([+-]?([0-9]*)(\(.|,)([0-9]+))?)$', event.raw_text)
                        number = match.group(1)
                        if number is not None:
                            await self.controller.next()
                        else:
                            await bot.send_message(telegram_chat_id, "**No valid Input for measure of original gravity found!**")

                if r'(?i).*moin' or r'(?i).*hi' or r'(?i).*h(a|e)llo' in event.raw_text:
                    sender = await event.get_sender()
                    await bot.send_message(telegram_chat_id, "Hi {}, use command /help to find a list of all commands.".format(sender))
                else:
                    sender = await event.get_sender()
                    await bot.send_message(telegram_chat_id, "Hi {}, I could not parse your text.".format(sender))

            # with bot:
                # bot.loop.run_until_disconnected()
            # await self.set_commands()
        pass

    # @bot.on(events.NewMessage(pattern='/help'))
    # async def help(event):
        # tmp=""
        # cmd_list = [{"command":"help","description":"get a list of all commands with description"},
                    # {"command":"next","description":"Next Brew Step"},
                    # {"command":"start","description":"start brewing"},
                    # {"command":"stop","description":"stop brewing"},
                    # {"command":"set_target","description":"set Target Temperature of the item you choose"},
                    # {"command":"get_target","description":"get Target Temperature of all items"},
                    # {"command":"get_timer","description":"get the actual countdown time"},
                    # {"command":"get_chart","description":"send Picture of chart from the item you choose"},
                    # {"command":"get_parameter","description":"get all parameters of the item you choose"}]
        # for items in cmd_list:
            # tmp=tmp+("/%s: %s\n" %(items["command"],items["description"]))
        # title= 'List of Commands:'
        # await bot.send_message(telegram_chat_id, "**{}** \{}".format(title,tmp))
        # raise events.Stoppropagation
        
        
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
            await bot.send_message(telegram_chat_id, "**{}** \{}".format(title,message))
            
            ##################################################
            # text = "<b>" + title + \
                # "</b>\n<i>" + message + "</i>"
            # url = "https://api.telegram.org/bot" + telegram_bot_token + "/sendMessage"
            # escapedUrl = requests.Request('GET', url,
                                        # params={"chat_id": telegram_chat_id,
                                                # "text": text,
                                                # "parse_mode": "HTML"},
                                        # ).prepare().url
            # requests.get(escapedUrl)

def setup(cbpi):
    cbpi.plugin.register("TelegramPushNotifications", Telegram)
    pass

