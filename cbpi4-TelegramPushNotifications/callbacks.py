
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
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from influxdb_client import InfluxDBClient
from datetime import datetime
from datetime import timedelta
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
                    await event.edit("Target_temp of {} is {}°{}.".format(item["name"],item["target_temp"],TEMP_UNIT))
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
                    buttons = [Button.inline("4h","4h"),Button.inline("12h","12h"),Button.inline("1d","24h"),Button.inline("1w","1w"),Button.inline("2w","2w"),Button.inline("3w","3w"),Button.inline("4w","4w"),Button.inline("6w","6w")]
                    await event.edit("**Choose timeframe for fermenter-chart: {}**".format(item["name"]),buttons=buttons)
            for item in kettles["data"]:
                if item["id"] in str(event.data):
                    buttons = [Button.inline("1h","1h"),Button.inline("2h","2h"),Button.inline("4h","4h"),Button.inline("6h","6h"),Button.inline("8h","8h"),Button.inline("12h","12h"),Button.inline("1d","24h"),Button.inline("2d","48h")]
                    await event.edit("**Choose timeframe for kettle-chart: {}**".format(item["name"]),buttons=buttons)
        elif "timeframe" in msg.message:
            for item in fermenter["data"]:
                if item["name"] in msg.message:
                    async with event.client.action(event.chat_id, 'photo') as action:
                        await TelegramCallbacks.gen_chart(item["id"],str(event.data))
                        await event.edit("Fermenter: {}".format(item["name"]))
                        await event.client.send_file(event.chat_id, file='./config/upload/fig1.png', progress_callback=action.progress)
            for item in kettles["data"]:
                if item["name"] in msg.message:
                    async with event.client.action(event.chat_id, 'photo') as action:
                        await TelegramCallbacks.gen_chart(item["id"],str(event.data))
                        await event.edit("Kettle: {}".format(item["name"]))
                        await event.client.send_file(event.chat_id, file='./config/upload/fig1.png', progress_callback=action.progress)
        else:
            noti = await TelegramCallbacks.get_items("notification/")
            s=str(event.data)[2:-1]
            json_acceptable_string = s.replace("'", "\"")
            data=json.loads(json_acceptable_string)
            
            for key in noti:
                if str(noti[key]) in str(event.data):
                    n_id=data["n"]
                    a_id=data["a"]
                    
            update_msg=msg.message.split('\n')
            await event.edit("**{}**\n__{}__".format(update_msg[0],update_msg[1]))
            await TelegramCallbacks.post_items("notification/{}/action/{}".format(n_id,a_id),"")
            await TelegramCallbacks.post_items("notification/{}".format(n_id),"")
        raise events.StopPropagation

    @events.register(events.NewMessage(pattern='/next'))
    async def next(event):
        # await self.controller.next()
        await TelegramCallbacks.post_items("step2/next","")
        await event.respond("Next step started!")
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
        steps = await TelegramCallbacks.get_items("step2/")
        found_paused_step = False
        found_active_step = False
        
        for value in steps["steps"]:
            if value["status"] == "P":
                found_paused_step = True
                await event.respond("Step '{}' resumed.".format(value["name"]))
            elif value["status"] == "A":
                found_active_step = True
                await event.respond("Step '{}' is already started.".format(value["name"]))
        if not found_paused_step and not found_active_step:
            await event.respond("brewing started!")
        await TelegramCallbacks.post_items("step2/start","")
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/stop'))
    async def stop(event):
        # await self.controller.stop()
        steps = await TelegramCallbacks.get_items("step2/")
        found_paused_step = False
        found_active_step = False
        
        for value in steps["steps"]:
            if value["status"] == "P":
                found_paused_step = True
                await event.respond("Step '{}' is already stopped.".format(value["name"]))
            elif value["status"] == "A":
                found_active_step = True
                await event.respond("Step '{}' stopped.".format(value["name"]))
        if not found_paused_step and not found_active_step:
            await event.respond("brewing is not active!")
        await TelegramCallbacks.post_items("step2/stop","")
        raise events.StopPropagation
    
    @events.register(events.NewMessage(pattern='/reset'))
    async def reset(event):
        # await self.controller.reset()
        steps = await TelegramCallbacks.get_items("step2/")
        found_paused_step = False
        found_active_step = False
        
        for value in steps["steps"]:
            if value["status"] == "P":
                found_paused_step = True
                await event.respond("brewing stopped!")
            elif value["status"] == "A":
                found_active_step = True
                await event.respond("Step '{}' need to be stopped before.".format(value["name"]))
        if not found_paused_step and not found_active_step:
            await event.respond("brewing is not active!")
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
        found_active_step = False
        
        for value in steps["steps"]:
            if value["status"] == "A":
                found_active_step = True
                if value["state_text"] is not "":
                    await event.respond("Additional information of active step '{}' is {}.".format(value["name"],value["state_text"]))
                else:
                    await event.respond("No additional information for active step '{}'".format(value["name"]))
            elif value["status"] == "P":
                found_active_step = True
                await event.respond("Step '{}' is paused.".format(value["name"]))
        if not found_active_step:
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
            await event.respond("Next step started!")
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
        if re.search(r"(?i)moin", event.raw_text) or re.search(r"(?i)h(e|a)llo", event.raw_text) or re.search(r"(?i)hi", event.raw_text):
            sender = await event.get_sender()
            await event.respond("Hi {}, use command /help to find a list of all commands.".format(sender.first_name))
        else:
            sender = await event.get_sender()
            await event.respond("Hi {}, I could not parse your text.".format(sender.first_name))

    async def gen_chart(id, time):
        influxdbcloud = await TelegramCallbacks.post_items("config/INFLUXDBCLOUD","")
        influxdbcloud=influxdbcloud[1:-1]
        influxdbaddr = await TelegramCallbacks.post_items("config/INFLUXDBADDR","")
        influxdbaddr=influxdbaddr[1:-1]
        influxdbport = await TelegramCallbacks.post_items("config/INFLUXDBPORT","")
        influxdbport=influxdbport[1:-1]
        influxdbname = await TelegramCallbacks.post_items("config/INFLUXDBNAME","")
        influxdbname=influxdbname[1:-1]
        influxdbuser = await TelegramCallbacks.post_items("config/INFLUXDBUSER","")
        influxdbuser=influxdbuser[1:-1]
        influxdbpwd = await TelegramCallbacks.post_items("config/INFLUXDBPWD","")
        influxdbpwd=influxdbpwd[1:-1]
        
        sensors=[]
        TEMP_UNIT = await TelegramCallbacks.post_items("config/TEMP_UNIT/","")
        TEMP_UNIT = TEMP_UNIT[1:-1]
        
        logfiles = await TelegramCallbacks.post_items("config/CSVLOGFILES","")
        logfiles=logfiles[1:-1]
        
        kettles = await TelegramCallbacks.get_items("kettle/")
        ket=None
        for item in kettles["data"]:
            if item["id"] == id:
                ket = item
                break
        fermenter = await TelegramCallbacks.get_items("fermenter/")
        ferm=None
        for item in fermenter["data"]:
            if item["id"] == id:
                ferm = item
                break
        sensor = await TelegramCallbacks.get_items("sensor/")
        for value in sensor["data"]:
            if ket is not None:
                if value["id"] == ket["sensor"]:
                    sensors.append(dict(name=value["name"],type="Act Temp",id=value["id"]))
                elif value["type"] == "KettleSensor":
                    if value["props"]["Kettle"] == id:
                        if value["props"]["Data"] == "TargetTemp":
                            sensors.append(dict(name=value["name"],type="Target Temp",id=value["id"]))
                        else:
                            sensors.append(dict(name=value["name"],type="Power",id=value["id"]))
            elif ferm is not None:
                if value["id"] == ferm["sensor"]:
                    sensors.append(dict(name=value["name"],type="Act Temp",id=value["id"]))
                elif value["type"] == "FermenterSensor":
                    if value["props"]["Fermenter"] == id:
                        if value["props"]["Data"] == "TargetTemp":
                            sensors.append(dict(name=value["name"],type="Target Temp",id=value["id"]))
                        else:
                            sensors.append(dict(name=value["name"],type="Power",id=value["id"]))

        timestr = "-" + time[2:-1]

        if influxdbcloud != "No":
            if influxdbaddr is not None or influxdbuser is not None or influxdbname is not None or influxdbpwd is not None:
                results = []
                client = InfluxDBClient(url="https://"+influxdbaddr, token=influxdbpwd, org=influxdbuser)
                query_api = client.query_api()
                for sens in sensors:
                    query = f'from(bucket: "{influxdbname}") |> range(start: duration(v: "{timestr}")) |> filter(fn: (r) => r["itemID"] == "{sens["id"]}")'
                    result = client.query_api().query(org=influxdbuser, query=query)

                    sensor = []
                    for table in result:
                        for record in table.records:
                            sensor.append([record.get_time(), record.get_value()])
                    
                    results.append(sensor)
        
        elif logfiles == "Yes":
            results = []
            now = datetime.now()
            if timestr[-1] == 'w':
                timeref = now - timedelta(weeks=int(timestr[1:-1]))
            elif timestr[-1] == 'h':
                timeref = now - timedelta(hours=int(timestr[1:-1]))
            for sens in sensors:
                log_data = await TelegramCallbacks.post_items("log/", '{"' + sens["id"] + '":""}')
                log_dict = json.loads(log_data)
                sensor = []
                if "error" not in log_dict:
                    for i, timestamp in enumerate(log_dict[sens["id"]]["time"]):
                        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                        if dt >= timeref:
                            sensor.append([timestamp,log_dict[sens["id"]]["value"][i]])
                    
                    results.append(sensor)

        if results:
            plt.style.use('dark_background')
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
            hfmt = matplotlib.dates.DateFormatter('%H:%M:%S')

            ax.xaxis.set_major_formatter(hfmt)
            if ket is not None:
                ax.set_title('Kettle: %s' % ket["name"])
            if ferm is not None:
                ax.set_title('Fermenter: %s' % ferm["name"])
            ax.set_xlabel('Time')
            ax.set_ylabel('Temperature in °'+TEMP_UNIT)
            ax.set_ylim(-10, 110)
            plt.setp(ax.get_xticklabels(), size=8)

            ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
            ax2.set_ylabel('Power in %')
            if ferm is not None:
                ax2.set_ylim(-1, 1)
                ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1.0))
            else:
                ax2.set_ylim(0, 100)
            lns = None
            for i, result in enumerate(results):
                x = [d[0] for d in result]
                xs = matplotlib.dates.date2num(x)
                y = [val[1] for val in result]
                if sensors[i]["type"] == "Power":
                    ln = ax2.plot(xs, y, color='g', drawstyle='steps-post', label=sensors[i]["type"])
                elif sensors[i]["type"] == "Target Temp":
                    ln = ax.plot(xs, y, color='r', drawstyle='steps-post', label=sensors[i]["type"])
                elif sensors[i]["type"] == "Act Temp":
                    ln = ax.plot(xs, y, color='tab:orange', label=sensors[i]["type"])
                else:
                    ln = ax.plot(xs, y, label=sensors[i]["type"])
                if i == 0:
                    lns = ln
                else:
                    lns += ln

            plt.grid()
            labs = [l.get_label() for l in lns]
            ax.legend(lns, labs, loc=0)
            fig.tight_layout()
            fig.savefig('./config/upload/fig1.png')
            plt.close(fig)
