#!/usr/bin/env python
#  -*- coding: utf-8 -*- 

# renv_device.py

import os, types, inspect, time, sys
import json
import websocket, logging
import uuid
import functools

from logging import getLogger

from mta_sdk import mtaDevice




class InvalidMessageError():
    """
    WebSocket受信メッセージが異常
    """
    def __init__(self, msg):
        self._msg = msg
        pass

    def __str__(self):
        return self._msg

class InvalidDocFormatError():
    """
    デバイス情報生成時にパースしたコメントブロックの文法エラー
    """
    def __init__(self, msg):
        self._msg = msg
        pass

    def __str__(self):
        return self._msg


def actionHandler(func):
    """ アクションハンドラ用デコレータ 
    """
    func._action_handler_method = True
    true_args, _, _, _ = inspect.getargspec(func)
    func._true_args = true_args

    @functools.wraps(func)
    def wrapper__(*args, **kwds):
        self = args[0]
        return_value = func(*args, **kwds)
        return return_value

    return wrapper__

def event(func):
    """ イベント送信用デコレータ """
    func.__event_method__ = True
    true_args, _, _, _ = inspect.getargspec(func)
    func._true_args = true_args

    @functools.wraps(func)
    def wrapper__(*args, **kwds):
        self = args[0]
        return_value = func(*args, **kwds)
        param = {}
        paramInfo_ = None
        ps = [cap for cap in self.deviceInfoText['capabilityList'] if cap['eventName'] == func.__name__[4:]]
        if len(ps) == 0:
            raise InvalidDocFormatError('Parsing Function call (%s) failed. Capability descriptor of this function can not be found.')
            
        paramInfos = ps[0]['paramInfo']
        for paramInfo in paramInfos:
            key = paramInfo['paramName']
            if not key in return_value.keys():
                raise InvalidDocFormatError('Parsing Function call (%s) failed. Return value does not contain %s member' % (func.__name__, key))

            typeStr = paramInfo['paramType']
            param[key] = {u'val': return_value[key], u'type': typeStr}

        if not return_value is None:
            name = func.__name__[4:]
            msg = {u'eventName': name,
                   u'eventSendDeviceName': unicode(self.name + ':' + self.version, 'euc-jp').decode('utf-8'),
                   # u'eventParam': return_value}
                   u'eventParam': param}
            json_str = json.dumps(msg)
            if len(self._ws) > 0:
                if self._use_mta:
                    self._mta.sendMessage(json_str)
                else:
                    self._ws[0].send(json_str)

    return wrapper__


def _parse_param(func_name, line_num, line, args):
    value = line[6:].strip()
    typeStr = value[: value.find(' ')+1].strip()
    value = value[value.find(' ')+1:]
    name = value.split()[0][:-1]
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

def _parse_doc(func_name, doc, args):
    param_parse = False
    outDoc = ''
    params = []
    delim = ''
    if func_name.startswith('on'):
        delim = 'param'
    elif func_name.startswith('send'):
        delim = 'return'

    if delim == '':
        raise InvalidDocFormatError('Invalid Function Name (%s)' % func_name)
    if doc is None or  len(doc.strip()) == 0:
        return 'No Comment', []

    for i, line in enumerate(doc.split('\n')):
        line = line.strip()
        if line.startswith(':') and line.split()[0][1:] == delim:
            params.append(_parse_param(func_name, i, line, args))
            param_parse = True
            continue

        if not param_parse:
            outDoc = outDoc + line
        pass
    return outDoc.strip(), params
            
class RenvDevice():
    """ Renvデバイス用の基本クラス 

    :param String typeId: タイプIDの文字列
    :param String name: デバイス名の文字列
    :param String version: バージョン番号の文字列
    """

    def __init__(self, typeId, name, version="1.0.0", device_uuid=None, use_mta=False, deviceName=None, logger=None):
        """ 
        イニシャライザ

        :param String typeId: タイプIDの文字列
        :param String name: デバイス名の文字列
        :param String version: バージョン番号の文字列
        """
        if logger is None:
            logging.basicConfig(filename="renv_device.log", format='%(levelname)s:%(asctime)s %(message)s')
        self._logger = logger or getLogger(__name__)
        

        self.info("RenvDevice.__init__(typeId=%s, name=%s, version=%s, use_mta=%s, deviceName=%s)" % (typeId, name, version, use_mta, deviceName))
        self.__typeId = typeId
        self.__name = name
        self.__version = version
        self.__uuid = device_uuid or str(uuid.uuid5(uuid.NAMESPACE_DNS, name + ':' + version))
        self._deviceName = name + ':' + version if deviceName is None else deviceName
        self._ws = []
        print('RenvDevice: UUID       = ' + (self.__uuid))
        print('RenvDevice: deviceName = ' + (self._deviceName))
        self.debug('RenvDevice: UUID       = ' + (self.__uuid))
        self.debug('RenvDevice: deviceName = ' + (self._deviceName))
        self._comment, params = _parse_doc('onInitialize', self.__doc__, [])
        self.deviceInfoText = self.getDeviceInfo()

        self._use_mta = use_mta
        if self._use_mta:
            print ('Using MTA: DeviceName = %s' % deviceName)
            self.debug('Using MTA: DeviceName = %s' % deviceName)
            text = json.dumps(self.deviceInfoText)
            self._mta = mtaDevice(name if deviceName is None else deviceName, firstMessage=text, logger=logger)
        pass

    def updateDeviceInfo(self):
        """ デバイス記述子を再構築する．RendDeviceクラスを継承したクラスを再度継承した場合に使う
        """
        self.info("RenvDevice.updateDeviceInfo()")
        self._comment = self.__doc__  # "deviceComment hogehoge" #_parse_doc('onInitialize', self.__doc__, [])
        self.deviceInfoText = self.getDeviceInfo()
        if self._use_mta:
            text = json.dumps(self.deviceInfoText)
            self._mta = mtaDevice(self.name, firstMessage=text)

        # print 'updateComment', self._comment

    @property
    def name(self):
        """ デバイス名 
        
        :return String: デバイス名 
        """
        return self.__name

    @property
    def version(self):
        """ バージョン番号の文字列 

        :return String: バージョン番号の文字列 
        """
        return self.__version
    
    @property
    def uuid(self):
        """ UUIDの文字列 

        :return String: UUID
        """
        return self.__uuid

    @property
    def typeId(self):
        """ タイプIDの文字列 

        :return String: タイプID
        """
        return self.__typeId

    def setWebSocket(self, ws):
        """ 
        ウェブソケットを外部で初期化する場合に使うメソッド

        :param ws: ウェブソケットオブジェクト
        """
        self.__ws = ws
        ws.on_message = self._on_message
        ws.on_close = self._on_close
        ws.on_error = self._on_error
        ws.on_open  = self._on_open

    def _dispatch_mta(self, payload):
        self._dispatch_message(payload)


    def connect(self, host, proxy_host=None, proxy_port=None):
        """ ウェブソケットを初期化して指定されたホストに接続する場合に使うメソッド

        :param String host: ホストのIPアドレス
        :param String proxy_host: プロキシのIP (省略可) *未対応
        :param String proxy_port: プロキシのポート番号 (省略可) *未対応
        """
        self.info("RenvDevice.connect(%s)" % host)
        self._host = host
        if self._use_mta:
            print ('Connecting to MTA: "ws://%s"' % host)
            self.info('Connecting to MTA: "ws://%s"' % host)
            self._mta.connectToMta("ws://" + host, self._dispatch_mta)

        else:
            print ('Conneting to R-env: "ws://%s"' % host)
            self.info('Conneting to R-env: "ws://%s"' % host)
            self.__ws = websocket.WebSocketApp("ws://" + host,
                                               on_message=self._on_message,
                                               on_close=self._on_close,
                                               on_error=self._on_error)
            self.__ws.on_open = self._on_open


        
    def run_forever(self):
        """ ウェブソケットの受信待ちポーリングを開始する．
        割り込みが起こるまで終了しない """
        self.info("RenvDevice.run_forever()")
        if self._use_mta:
            self._mta.run_forever()
        else:
            self.__ws.run_forever()

    def execute(self):
        """ 実行．何もしない """
        pass

    def _on_open(self, ws):
        """ 接続された場合に呼ばれるイベントハンドラ 
        """
        print("Connecting to host.")
        self.info("RenvDevice._on_open()")
        self.info("Now Connecting To Host.")
        # デバイス記述情報を生成して送信する
        text = json.dumps(self.deviceInfoText)
        print ("Sending DeviceInfo")
        # print (text)
        self._ws.append(ws)
        self.__ws.send(text)
        pass

    def _on_close(self, ws):
        """ 切断されたときに呼ばれるイベントハンドラ 
        """
        self.info("RenvDevice._on_close()")
        pass

    def _on_message(self, ws, message):
        """ 
        メッセージ到着時に呼ばれるイベントハンドラ 
        
        :param WebSocket ws:
        :param Dictionary message: 
        """
        self.debug("RenvDevice._on_message:%s" % message)
        # メッセージを解析して対応するアクションハンドラを呼ぶ
        self._dispatch_message(message)
        pass

    def _on_error(self, ws, error):
        """ エラー時のイベントハンドラ """
        self.error(error)
        pass

    def info(self, msg):
        self._logger.info(msg)

    def debug(self, msg):
        self._logger.debug(msg)

    def error(self, msg):
        self._logger.error(msg)

    def _call_action_handler(self, key, msg):
        """ 受信したJSONパラメータを使ってアクションハンドラを呼び出す
        
        :param String key: アクションハンドラの名前
        :param Dictionary msg: 受信したJSONメッセージ
        """
        self.info("RenvDevice._call_action_handler(%s, %s)" % (key, msg))
        params = {}
        args = getattr(self, key)._true_args
        args = args[1:]
        # 引数名と受け取ったデータのラベルの対応づけをする
        for arg_name in args:
            arg_name = unicode(arg_name, 'utf-8').decode('utf-8')
            if not arg_name in msg['eventParam'].keys():
                print('No action (name=%s) is found.' % (arg_name))
                self.error('No action (name=%s) is found.' % (arg_name))
                raise InvalidMessageError('EventType(' + key[2:] + ') parameter is invalid. ' +
                                          'Parameter(name="' + arg_name + '") does not found. ' +
                                          'msg["eventParam"] is :' + str(msg['eventParam']))
            
            # 該当する引数名が受信したオブジェクトの中にあったら，それを辞書に加える
            param = msg['eventParam'][arg_name]
            params[arg_name] = param['val']
        self.debug('Calling action_handler(name=%s)' % (key))
        retval = getattr(self, key)(**params) # 辞書を引数とした関数コールを行う
        return retval


    def _check_action_handler(self, key, eventName=None):
        """ Keyで表される関数がアクションハンドラ関数かをチェックする
        
        :param String key: 対象となるキー
        :param String eventName: 省略可能．イベント名が分かっているなら渡すと，対応するイベントのアクションハンドラか否かを返す
        """
        # self.info('RenvDevice._check_action_handler(%s, %s)' % (key, eventName))
        if type(getattr(self, key)) == types.MethodType or type(getattr(self, key)) == types.FunctionType:
            if key.startswith('on'):
                if eventName != None:
                    if eventName == key[2:]:
                        # self.debug('Found Action Handler (%s, %s)' % (key, eventName))
                        return True
                    else:
                        # self.debug('Not Found Action Handler (%s, %s)' % (key, eventName))
                        return False
                # self.debug('Found Action Handler (%s, %s)' % (key, eventName))
                return True
        # self.debug('Not Found Action Handler (%s, %s)' % (key, eventName))
        return False
        
    def _dispatch_message(self, message):
        """ メッセージ到着時に呼ばれる．メッセージを解析してアクションハンドラを起動する """
        self.info('RenvDevice._dispatch_message()')
        self.debug('message is %s' % message)
        msg = json.loads(message)

        # Start Transport イベントは無視する
        if str(msg['eventName']) == 'Renv.System.StartTransportEvent':
            return

        # 自分自身のインスタンスメソッド (もしくは後付けのメソッドメンバ) を解析する
        for key in dir(self): 
            # まず，関数かどうか確認する
            if self._check_action_handler(key, msg['eventName']):
                return self._call_action_handler(key, msg)
            pass
        self.error(' - Can not find ActionHandler for msg (%s)\n' % str(msg['eventName']))
        self.error(msg)
        pass

    def event(self, eventName, data):
        """ イベントの強制送信用の関数．カスタムイベント時などに使う

        :param String eventName: イベント名
        :param Dictionary data: データ．eventParamにセットされます．ディクショナリ型 
        """
        self.info('RenvDevice.event(eventName=%s)' % eventName)
        self.debug('Data is %s' % data)
        self.debug('Use mta = %s' % self._use_mta)
        msg = {
            u'eventName': eventName,
            u'eventParam': data,
            u'eventSendDeviceName': unicode(self.name + ':' + self.version, 'euc-jp').decode('utf-8')
            }
        text = json.dumps(msg)
        if len(self._ws) > 0 and not self._use_mta:
            self._ws[0].send(text)
        elif self._use_mta:
            self._mta.sendMessage(text)



    def getDeviceInfo(self):
        """ 
        コメント文字列からデバイス記述子を生成する 

        :return Dictionary: デバイス記述子
        """
        self.info("RenvDevice.getDeviceInfo()")
        capabilities = []
        # RenvDeviceクラスオブジェクトのメンバを解析する
        for key in dir(self):
            # もしメンバがアクションハンドラならば
            if self._check_action_handler(key):
                # 関数のドキュメントからCapability辞書を作成して登録する
                args = getattr(self, key)._true_args
                args = args[1:] # fist one is self
                hasParam = len(args) > 0
                doc = getattr(self, key).__doc__
                docInfo, paramInfo = _parse_doc(key, doc, args)
                capability = {
                    "eventName" : key[2: ],
                    "eventType" : "In",
                    "eventComment" : docInfo,
                    # "hasParam" : hasParam,
                    "paramInfo" : paramInfo
                    }

                # 同じイベントがすでに登録されていたら例外を送る
                if key[2:] in [c['eventName'] for c in capabilities]:
                    raise InvalidDocFormatError('Same Key is detected ("' + key[2: ] + '")')

                # イベントの追加
                capabilities.append(capability)

            # もしメンバがイベント送信メソッドなら
            elif (key.startswith('send') and type(getattr(self, key)) == types.MethodType):
                # 関数のドキュメントからCapability辞書を作成して登録する
                args = getattr(self, key)._true_args
                args = args[1:] # first one is self
                hasParam = len(args) > 0
                funcObj = getattr(self, key)
                doc = funcObj.__doc__
                docInfo, paramInfo = _parse_doc(key, doc, args)
                capability = {
                    "eventName" : key[4: ],
                    "eventType" : "Out",
                    "eventComment" : docInfo,
                    "hasParam" : hasParam,
                    "paramInfo" : paramInfo
                    }
                # setattr(funcObj, '_paramInfo', paramInfo)

                if key[4:] in [c['eventName'] for c in capabilities]:
                    raise InvalidDocFormatError('Same Key is detected ("' + key[4: ] + '")')

                capabilities.append(capability)

                
        deviceInfo = {"deviceTypeId": self.typeId,
                "deviceId": self.uuid,
                "deviceComment" : self._comment,
                "deviceName": self.name + ':' + self.version if self._deviceName is None else self._deviceName,
                "capabilityList": capabilities }

        self.info("DeviceInfo:%s" % deviceInfo)
        return deviceInfo

    
