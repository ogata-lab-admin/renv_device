#!/usr/bin/env python
#  -*- coding: utf-8 -*- 

import os, types, inspect, time
import json
import websocket, logging
import uuid
#import uni_text
import functools

logging.basicConfig()

def eventHandler(func):
    func._event_handler_method = True
    true_args, _, _, _ = inspect.getargspec(func)
    func._true_args = true_args

    @functools.wraps(func)
    def wrapper__(*args, **kwds):
        self = args[0]
        return_value = func(*args, **kwds)

    return wrapper__

def event(func):
    func.__event_method__ = True
    true_args, _, _, _ = inspect.getargspec(func)
    func._true_args = true_args

    @functools.wraps(func)
    def wrapper__(*args, **kwds):
        self = args[0]
        return_value = func(*args, **kwds)
        
        pkt = {'eventName': name}
        if not return_value is None:
            json_str = json.dumps(return_value)
        self.send(json_str)

    return wrapper__

class InvalidMessageError():
    def __init__(self, msg):
        self._msg = msg
        pass

    def __str__(self):
        return self._msg

class InvalidDocFormatError():
    def __init__(self, msg):
        self._msg = msg
        pass

    def __str__(self):
        return self._msg

def parse_param(func_name, line_num, line, args):
    value = line[6:].strip()
    typeStr = value[value.find('{')+1: value.find('}')].strip()
    value = value[value.find('}')+1:]
    name = value.split()[0]
    if not name in args:
        raise InvalidDocFormatError('Parsing function (' + func_name + ') in comment: Line(' + str(line_num) + ') param name "' + name + '" not found' +
                                    'Params are :' + str(args))
    
    value = value[len(name)+1:].strip()

    limitation = 'SelectForm' if value.find('[') >= 0 else 'FreeForm'
    comment = value if value.find('[') < 0 else value[:value.find('[')].strip()
    
    altInfos = []
    if limitation == 'SelectForm':
        value = value[value.find('[')+1: value.find(']')]
        for arg_alt_info in [v.strip() for v in value.split('|')]:
            if arg_alt_info.find(':') < 0:
                raise InvalidDocFormatError('Parsing function(' + func_name + ') in comment: Line(' + str(line_num) + ') selection value does not have comment.' + 
                                            'Params are : ' + str(args))
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

def parse_doc(func_name, doc, args):
    param_parse = False
    outDoc = ''
    params = []
    for i, line in enumerate(doc.split('\n')):
        line = line.strip()
        if line.startswith('@') and line.split()[0][1:] == 'param':
            params.append(parse_param(func_name, i, line, args))
            param_parse = True
            continue

        if not param_parse:
            outDoc = outDoc + line
        pass
    return outDoc.strip(), params
            
class RenvDevice():

    def __init__(self, typeId, name, version="1.0.0"):
        self.__typeId = typeId
        self.__name = name
        self.__version = version
        self.__uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, name + ':' + version))
        self._ws = []
        print ('RenvDevice: Generated UUID = ' + (self.__uuid))
        self.deviceInfoText = self.getDeviceInfo()
        pass

    @property
    def name(self):
        return self.__name

    @property
    def version(self):
        return self.__version
    
    @property
    def uuid(self):
        return self.__uuid

    @property
    def typeId(self):
        return self.__typeId

    def setWebSocket(self, ws):
        self.__ws = ws
        ws.on_message = self._on_message
        ws.on_close = self._on_close
        ws.on_error = self._on_error
        ws.on_open  = self._on_open

    def connect(self, host, proxy_host=None, proxy_port=None):
        self.__ws = websocket.WebSocketApp("ws://" + host,
                                           on_message=self._on_message,
                                           on_close=self._on_close,
                                           on_error=self._on_error)
        self.__ws.on_open = self._on_open
        
    def run_forever(self):
        self.__ws.run_forever()

    def execute(self):
        print 'on_execute'
        pass

    def _on_open(self, ws):
        print '_on_open'
        text = json.dumps(self.deviceInfoText)
        
        self._ws.append(ws)
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
        msg = json.loads(message)
        print msg
        for key in dir(self):
            if key.startswith('on') and type(getattr(self, key)) == types.MethodType and msg['eventName'] == key[2:]:
                params = {}
                # self._log(""" Found Method corresponding to event. Let's parse argument. """)
                args = getattr(self, key)._true_args
                args = args[1:]
                for arg_name in args:
                    arg_name = unicode(arg_name, 'utf-8').decode('utf-8')
                    if not arg_name in msg['eventParam'].keys():

                        raise InvalidMessageError('EventType(' + key[2:] + ') parameter is invalid. ' +
                                                  'Parameter(name="' + arg_name + '") does not found. ' +
                                                  'msg["eventParam"] is :' + str(msg['eventParam']))
                        
                    param = msg['eventParam'][arg_name]
                    params[arg_name] = param['val']

                retval = getattr(self, key)(**params)
                pass
            pass

        pass


    def event(self, eventName, data):
        msg = {
            u'eventName': unicode(eventName, 'euc-jp').decode('utf-8'), 
            u'eventParam': data,
            u'eventSendDeviceName': unicode(self.name + ':' + self.version, 'euc-jp').decode('utf-8')
            }
        # print 'Device.ecent', msg, len(self._ws)
        text = json.dumps(msg)
        print text
        if len(self._ws) > 0:
            self._ws[0].send(text)

    def getDeviceInfo(self):
        capabilities = []
        for key in dir(self):
            if (key.startswith('on') and type(getattr(self, key)) == types.MethodType):
                #args, _, _, _ = inspect.getargspec(getattr(self, key))
                args = getattr(self, key)._true_args
                args = args[1:] # fist one is self
                hasParam = len(args) > 0
                doc = getattr(self, key).__doc__
                docInfo, paramInfo = parse_doc(key, doc, args)
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
                # args, _, _, _ = inspect.getargspec(getattr(self, key))
                args = getattr(self, key)._true_args
                args = args[1:] # first one is self
                hasParam = len(args) > 0
                doc = getattr(self, key).__doc__
                docInfo, paramInfo = parse_doc(key, doc, args)
                capability = {
                    "eventName" : key[4: ],
                    "eventType" : "Out",
                    "eventComment" : docInfo,
                    "hasParam" : hasParam,
                    "paramInfo" : paramInfo
                    }
                

                if key[4:] in [c['eventName'] for c in capabilities]:
                    raise InvalidDocFormatError('Same Key is detected ("' + key[4: ] + '")')

                capabilities.append(capability)


        return {"deviceTypeId": self.typeId,
                "deviceId": self.uuid,
                "deviceName": self.name + ':' + self.version,
                "capabilityList": capabilities }

    
