#!/usr/bin/env
#  -*- coding: utf-8 -*- 

import os, types, inspect
import json
import websocket

class InvalidDocFormatError():
    def __init__(self, msg):
        self._msg = msg
        pass

    def __str__(self):
        return self._msg

def parse_param(line_num, line, args):
    value = line[6:].strip()
    typeStr = value[value.find('{')+1: value.find('}')].strip()
    value = value[value.find('}')+1:]
    name = value.split()[0]
    if not name in args:
        raise InvalidDocFormatError('Line(' + str(line_num) + ') param name "' + name + '" not found')
    value = value[len(name)+1:].strip()

    limitation = 'SelectForm' if value.find('[') >= 0 else 'FreeForm'
    comment = value if value.find('[') < 0 else value[:value.find('[')].strip()
    
    altInfos = []
    if limitation == 'SelectForm':
        value = value[value.find('[')+1: value.find(']')]
        for arg_alt_info in [v.strip() for v in value.split('|')]:
            if arg_alt_info.find(':') < 0:
                raise InvalidDocFormatError('Line(' + str(line_num) + ') selection value does not have comment.')
            tokens = arg_alt_info.split(':')
            altInfos.append({
                    "paramData" : tokens[0].strip(),
                    "paramComment" : tokens[1].strip() })
        
            pass
        pass
    info = {
        "paramName" : name,
        "paramType" : typeStr,
        "paramComment" : comment,
        "paramLimitation" : limitation,
        }
    if limitation == "SelectForm":
        info["paramElements"] = altInfos
    return info

def parse_doc(doc, args):
    param_parse = False
    outDoc = ''
    params = []
    for i, line in enumerate(doc.split('\n')):
        line = line.strip()
        if line.startswith('@') and line.split()[0][1:] == 'param':
            params.append(parse_param(i, line, args))
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
        capabilities = []
        for key in dir(self):
            if (key.startswith('on') and type(getattr(self, key)) == types.MethodType):
                args, _, _, _ = inspect.getargspec(getattr(self, key))
                args = args[1:] # fist one is self
                hasParam = len(args) > 0
                doc = getattr(self, key).__doc__
                docInfo, paramInfo = parse_doc(doc, args)
                capability = {
                    "eventName" : key[2: ],
                    "eventType" : "In",
                    "eventComment" : docInfo,
                    "hasParam" : hasParam,
                    "paramInfo" : paramInfo
                    }

                if key[2:] in [c['eventName'] for c in capabilities]:
                    raise InvalidDocFormatError('Same Key is detected ("' + key[2: ] + '")')


                capabilities.append(capability)

            elif (key.startswith('send') and type(getattr(self, key)) == types.MethodType):
                args, _, _, _ = inspect.getargspec(getattr(self, key))
                args = args[1:] # first one is self
                hasParam = False
                docInfo, paramInfo = parse_doc(doc, args)
                capability = {
                    "eventName" : key[4: ],
                    "eventType" : "Out",
                    "eventComment" : docInfo,
                    "hasParam" : hasParam }
                
                #print [c['eventName'] for c in capabilities]

                if key[4:] in [c['eventName'] for c in capabilities]:
                    raise InvalidDocFormatError('Same Key is detected ("' + key[4: ] + '")')
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
                    "hasParam": False }, 
                {
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


    
