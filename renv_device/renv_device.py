#!/usr/bin/env
#  -*- coding: utf-8 -*- 

import os, types, inspect
import json
import websocket

def parse_param(line):
    value = line[6:].strip()
    typeStr = value[value.find('{')+1: value.find('}')].strip()
    value = value[value.find('}')+1:]
    comment = value.find('[') < 0 ? value : value[:value.find('[')].strip()
    paramstr = 
    return value

def parse_doc(doc):
    param_parse = False
    outDoc = ''
    params = []
    for line in doc.split('\n'):
        line = line.strip()
        if line.startswith('@'):
            params.append(parse_param(line))
            param_parse = True
            continue

        if not param_parse:
            outDoc = outDoc + line

        pass
    return outDoc.strip(), params
            
class RenvDevice():

    def __init__(self, typeId, uuid, name):
        self.__typeId = typeId
        self.__uuid = uuid
        self.__name = name

        pass

    @property
    def name(self):
        return self.__name
    
    @property
    def id(self):
        return self.__uuid

    @property
    def typeId(self):
        return self.__typeId


    def connect(self, host, proxy_host=None, proxy_port=None):
        self.__ws = websocket.WebSocketApp(#)
        #self.__ws.connect(
            "ws://" + host, #http_proxy_host=proxy_host, http_proxy_port=proxy_port, 
                          on_message=self._on_message,
                          #on_open=self._on_open,
                          on_close=self._on_close,
                          on_error=self._on_error)
        self.__ws.on_open = self._on_open

    def run(self):
        self.__ws.run_forever()


    def _on_open(self, ws):
        text = json.dumps(self.deviceInfoText)
        self.__ws.send(text)

        pass


    def _on_close(self, ws):
        pass


    def _on_message(self, ws, message):
        self._dispatch_message(message)
        pass


    def _on_error(self, ws, error):
        self._log(error)
        pass

    def _log(self, val):
        print val
        pass

    def _dispatch_message(self, message):
        print message

    def getDeviceInfo(self):

        for key in dir(self):
            capabilities = []
            if (key.startswith('on') and type(getattr(self, key)) == types.MethodType):
                args, _, _, _ = inspect.getargspec(getattr(self, key))
                args = args[1:] # fist one is self

                doc = getattr(self, key).__doc__
                docInfo, paramInfo = parse_doc(doc)
                capability = {
                    "eventName" : key[2: ],
                    "eventType" : "In",
                    "eventComment" : docInfo,
                    "hasParam" : len(args) > 0,
                    "paramInfo" : paramInfo
                    }
                
                print capability
                capabilities.append(capability)


        return {"deviceTypeId": self.typeId,
                "deviceId": self.id,
                "deviceName": self.name,
                "capabilityList": capabilities }


    val = {    
    "capabilityList": [
                {
                    "eventName": "ChangeColorRequest",
                    "eventType": "Out",
                    "eventComment": "エリア色変更要求",
                    "hasParam": False }, {
                    "eventName": "ChangeColorResponse",
                    "eventType": "In",
                    "eventComment": "エリア色変更結果",
                    "hasParam": True,
                    "paramInfo": [{"paramName":"area", 
                                   "paramComment":"エリア指定", 
                                   "paramType":"String",
                                   "paramLimitation":"SelectForm", 
                                   "paramElements": [{"paramData":"area1",
                                                      "paramComment":"エリア１"},
                                                     {"paramData":"area2",
                                                      "paramComment":"エリア２"}]},
                                  {"paramName":"color", 
                                   "paramComment":"色指定", 
                                   "paramType":"String",
                                   "paramLimitation":"SelectForm",
                                   "paramElements":[{"paramData":"red","paramComment":"赤"},
                                                    {"paramData":"blue","paramComment":"青"},
                                                    {"paramData":"white","paramComment":"白"}]}
                            ]}, 
                {
                    "eventName": "ChangeSceneRequest",
                    "eventType": "Out",
                    "eventComment": "シーン変更要求",
                    "hasParam": False }, {
                    "eventName": "ChangeSceneResponse",
                    "eventType": "In",
                    "eventComment": "シーン変更結果",
                    "hasParam": True,
                    "paramInfo": [{"paramName":"scene", "paramComment":"シーン状態", "paramType":"String",
                                   "paramLimitation":"SelectForm","paramElements":[{"paramData":"scene1","paramComment":"シーン１"},{"paramData":"scene2","paramComment":"シーン２"}]}
                                  ]}
                ]
                }


    
