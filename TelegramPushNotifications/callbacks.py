
# -*- coding: utf-8 -*-
import os
import aiohttp
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
from telethon import *
import re
import random
import json
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

class TelegramCallbacks(CBPiExtension):

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self.controller : StepController = cbpi.step

    @events.register(events.CallbackQuery)
    async def callbackQuery(event):
        msg = await event.get_message()
        TEMP_UNIT = await TelegramCallbacks.post_items("config/TEMP_UNIT/","")
        TEMP_UNIT = TEMP_UNIT[1:-1]
        kettles = await TelegramCallbacks.get_items("kettle/")
        fermenter = await TelegramCallbacks.get_items("fermenter/")
        if "get_target_temp" in msg.message:
            for item in fermenter["data"]:
                if item["id"] in str(event.data):
                    await event.edit("Target_temp of {} is {}°{}.".format(item["name"],item["target_temp"],TEMP_UNIT))
            for item in kettles["data"]:
                if item["id"] in str(event.data):
                    await event.edit("Target_temp of {} {}°{}.".format(item["name"],item["target_temp"],TEMP_UNIT))
        elif "set_target_temp" in msg.message:
            for item in fermenter["data"]:
                if item["id"] in str(event.data):
                    await event.edit("Enter the new target temperature for {}:".format(item["name"]))
            for item in kettles["data"]:
                if item["id"] in str(event.data):
                    await event.edit("Enter the new target temperature for {}:".format(item["name"]))
        elif "get_parameter" in msg.message:
            for item in fermenter["data"]:
                if item["id"] in str(event.data):
                    heater = ""
                    cooler = ""
                    # actors = self.cbpi.actor.get_state()
                    # sensors = self.cbpi.sensor.get_state()
                    sensor = await TelegramCallbacks.get_items("sensor/"+item["sensor"])
                    actor = await TelegramCallbacks.get_items("actor/")
                    for act in actor["data"]:
                        if act["id"] in item["heater"]:
                            heater = act["state"]
                        if act["id"] in item["cooler"]:
                            cooler = act["state"]
                    await event.edit("**{}**:\nbrewname: {}\nTarget-Temp: {}°{}\nSensor-Temp: {}°{}\nAutomatic: {}\nHeater: {}\nCooler: {}".format(item["name"],
                    item["brewname"],item["target_temp"],TEMP_UNIT,sensor["value"],TEMP_UNIT,item["state"],heater,cooler))
            for item in kettles["data"]:
                if item["id"] in str(event.data):
                    heater = ""
                    heater_power = ""
                    agitator = ""
                    sensor = await TelegramCallbacks.get_items("sensor/"+item["sensor"])
                    actor = await TelegramCallbacks.get_items("actor/")
                    for act in actor["data"]:
                        if act["id"] in item["heater"]:
                            heater = act["state"]
                            heater_power = act["power"]
                        if act["id"] in item["agitator"]:
                            agitator = act["state"]
                    await event.edit("**{}**:\nTarget-Temp: {}°{}\nSensor-Temp: {}°{}\nAutomatic: {}\nHeater: {}\nPower: {}%\nAgitator: {}".format(item["name"],
                    item["target_temp"],TEMP_UNIT,sensor["value"],TEMP_UNIT,item["state"],heater,heater_power,agitator))
        elif "get_chart" in msg.message:
            for item in fermenter["data"]:
                if item["id"] in str(event.data):
                    await event.edit("Charts are not implemented, yet! But will probably need influxdb and grafana.")
            for item in kettles["data"]:
                if item["id"] in str(event.data):
                    await event.edit("Charts are not implemented, yet! But will probably need influxdb and grafana.")
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/next'))
    async def next(event):
        # await self.controller.next()
        await TelegramCallbacks.post_items("step2/next","")
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/help'))
    async def help(event):
        bot = event.client
        chat_id = event.chat_id
        tmp=""
        cmd_list = [{"command":"help","description":"get a list of all commands with description"},
                    {"command":"next","description":"Next Brew Step"},
                    {"command":"start","description":"start brewing"},
                    {"command":"stop","description":"stop brewing"},
                    {"command":"reset","description":"reset brewing"},
                    {"command":"set_target","description":"set Target Temperature of the item you choose"},
                    {"command":"get_target","description":"get Target Temperature of all items"},
                    {"command":"get_step_info","description":"get infos of the active step"},
                    {"command":"get_chart","description":"send Picture of chart from the item you choose"},
                    {"command":"get_parameter","description":"get all parameters of the item you choose"}]
        for items in cmd_list:
            tmp=tmp+("/%s: %s\n" %(items["command"],items["description"]))
        title= 'List of Commands:'
        await event.respond("**{}** \n__{}__".format(title,tmp))
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/start'))
    async def start(event):
        # await self.controller.start()
        await TelegramCallbacks.post_items("step2/start","")
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/stop'))
    async def stop(event):
        # await self.controller.stop()
        await TelegramCallbacks.post_items("step2/stop","")
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/reset'))
    async def reset(event):
        # await self.controller.reset()
        await TelegramCallbacks.post_items("step2/reset","")
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/set_target'))
    async def setTarget(event):
        buttons = await TelegramCallbacks.gen_buttons()
        await event.respond("**Choose Item for set_target_temp**",buttons=buttons)
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/get_target'))
    async def getTarget(event):
        buttons = await TelegramCallbacks.gen_buttons()
        await event.respond("**Choose Item for get_target_temp**",buttons=buttons)
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/get_step_info'))
    async def getStepInfo(event):
        # steps = self.cbpi.step.get_state()
        steps = await TelegramCallbacks.get_items("step2/")
        for value in steps["steps"]:
            if value["status"] == "A":
                if value["state_text"] is not "":
                    await event.respond("Additional information of active step '{}' is {}.".format(value["name"],value["state_text"]))
                else:
                    await event.respond("No additional information for active step '{}'".format(value["name"]))
            elif value["status"] == "P":
                await event.respond("Step '{}' is paused.".format(value["name"]))
            else:
                await event.respond("No active step.")
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/get_chart'))
    async def getChart(event):
        buttons = await TelegramCallbacks.gen_buttons()
        await event.respond("**Choose Item for get_chart**",buttons=buttons)
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/get_parameter'))
    async def getParams(event):
        buttons = await TelegramCallbacks.gen_buttons()
        await event.respond("**Choose Item for get_parameter**",buttons=buttons)
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern=r".*(°P|Brix).*"))
    async def gravity(event):
        match = re.match(r'^([0-9]+(\.[0-9])?(°P| Brix))', event.raw_text)
        if match is not None:
            gravity = match.group(1)
            logger.info(gravity)
            # await self.controller.next()
            await TelegramCallbacks.post_items("step2/next","")
        else:
            await event.respond("**No valid Input for original gravity found!**(Please use Format XX.X°P or XX.X Brix)")
        raise events.StopPropagation
        
    async def gen_buttons():
        buttons = []
        kettles = await TelegramCallbacks.get_items("kettle/")
        fermenter = await TelegramCallbacks.get_items("fermenter/")
        for value in kettles["data"]:
            buttons.append(Button.inline(value["name"],value["id"]))
        for value in fermenter["data"]:
            buttons.append(Button.inline(value["name"],value["id"]))
        return buttons
    
    async def get_items(name):
        res = " "
        url="http://127.0.0.1:8000/"+name
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                res = await response.text()
                # logger.info(res)
                return json.loads(res)
    
    async def post_items(name,postdata):
        # logger.warning(postdata)
        url="http://localhost:8000/"+name
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=postdata, headers={"Content-Type": 'application/json','User-Agent': "TelegramPlugin"}) as response:
                return await response.text()
    
    @events.register(events.NewMessage(pattern=r".*°(C|F)$"))
    async def inputTemp(event):
        kettles = await TelegramCallbacks.get_items("kettle/")
        fermenter = await TelegramCallbacks.get_items("fermenter/")
        TEMP_UNIT = await TelegramCallbacks.post_items("config/TEMP_UNIT/","")
        TEMP_UNIT = TEMP_UNIT[1:-1]
        # TEMP_UNIT=self.cbpi.config.get("TEMP_UNIT", "C")
        # kettles = self.cbpi.kettle.get_state()
        # fermenter = self.cbpi.fermenter.get_state()
        match = re.match(r'^(([+-])?[0-9]+(\.[0-9])?°(C|F))', event.raw_text)
        msg = await event.client.get_messages(event.chat, ids=int(event.message.id)-1)
        if match is not None:
            number = match.group(1)
            if 'F' in TEMP_UNIT:
                temp = round(9.0 / 5.0 * float(number[:-2]) + 32, 2)
            else:
                temp = float(number[:-2])
            for item in fermenter["data"]:
                if item["name"] in msg.message:
                    await TelegramCallbacks.post_items("fermenter/"+item["id"]+"/target_temp",json.dumps( {"temp": temp}))
                    await event.respond("Set Target_temp of {} to {}°{}.".format(item["name"],temp,TEMP_UNIT))
            for item in kettles["data"]:
                if item["name"] in msg.message:
                    await TelegramCallbacks.post_items("kettle/"+item["id"]+"/target_temp",json.dumps( {"temp": temp}))
                    await event.respond("Set Target_temp of {} to {}°{}.".format(item["name"],temp,TEMP_UNIT))
                    # await self.set_target_temp(item["id"],temp)
        else:
            await event.respond("**No valid Input for Set Target_temp of {} found!**(Please use Format +-XXX°C or +-XXX°F)".format("STEP ABC"))
        raise events.StopPropagation

    @events.register(events.NewMessage)
    async def new_message_handler(event):
        # if event.is_reply:
            # replied = await event.get_reply_message()
            # sender = replied.sender
            # logger.warning(replied)
            # logger.warning(sender)
        if re.search(r"(?i)moin", event.raw_text) or re.search(r"(?i)h(e|a)llo", event.raw_text) or re.search(r"(?i)hi", event.raw_text):
            sender = await event.get_sender()
            await event.respond("Hi {}, use command /help to find a list of all commands.".format(sender.first_name))
        else:
            sender = await event.get_sender()
            await event.respond("Hi {}, I could not parse your text.".format(sender.first_name))
