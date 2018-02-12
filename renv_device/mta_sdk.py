import websocket
import bitstring
from logging import getLogger

class mtaDevice:

    def __init__(self, deviceName, firstMessage=None, logger=None):
        """
        deviceName   : Device Name to register with MTA
                        only pattern [0-9a-zA-Z-_]+ allowed
        firstMessage : Message(utf-8 str) to send when connecting to MTA
                        ex. deviceInfo
        """
        self._deviceName = deviceName
        self._firstMessage = firstMessage

        self._logger = logger or getLogger(__name__)


    def info(self, msg):
        self._logger.info(msg)

    def debug(self, msg):
        self._logger.debug(msg)

    def error(self, msg):
        self._logger.error(msg)

    def connectToMta(self, host, func=None):
        """
        connect to MTA info

        host    : MTA Uri (ex: MTAIpAddr:MTAIpPort)
        func    : CallBack function when receiveing message.
                    only one argument(message)
        """
        self.info("mtaDevice.connectToMta(%s, %s)" % (host, str(func)))
        self._ws = websocket.WebSocketApp(host, # + "/",
#                                            on_open = self._on_open,
                                            on_message = self._on_message,
                                            on_close=self._on_close,
                                            on_error=self._on_error)
        self._ws.on_open = self._on_open
        self._dispatchFunction = func
        pass

    def _on_open(self, ws):
        """
        when connect to MTA, mta_sdk send deviceName and firstMessage 
        """
        self.info("mtaDevice._on_open(%s)" % str(ws))
        self._ws.send(self._deviceName)
        if self._firstMessage is not None:
            self.debug("Sending DeviceInfo: %s" % self._firstMessage)
            self.sendMessage(self._firstMessage)
        pass

    def _on_message(self, ws, message):
        """
        receive message(binary) from MTA
        dispatch only payload(utf-8 str) included in message to CallBack Function

        message format : 
            aplication Identifier length (1byte)
            deviceIdentifier length (1byte)
            payload length (4byte)
            aplication Identifier
            deviceIdentifier
            payload
        """
        self.info("mtaDevice._on_message(%s)" % message)
        if self._dispatchFunction is not None:
            byteMessage = bitstring.BitStream(bytes=message, length=len(message)*8)

            startIndex = 0
            aplIdByteLength = byteMessage[startIndex : startIndex + 8].int
            startIndex += 8
            devIdByteLength = byteMessage[startIndex : startIndex + 8].int
            startIndex += 8
            payloadByteLength = byteMessage[startIndex : startIndex + 32].int
            startIndex += 32

            aplIdBitLength = aplIdByteLength * 8
            devIdBitLength = devIdByteLength * 8
            payloadBitLength = payloadByteLength * 8

            aplId = byteMessage[startIndex : startIndex + aplIdBitLength].bytes
            startIndex += aplIdBitLength
            devId = byteMessage[startIndex : startIndex + devIdBitLength].bytes
            startIndex += devIdBitLength
            payload = byteMessage[startIndex : startIndex + payloadBitLength].bytes

            self._dispatchFunction(payload)

        pass

    def _on_error(self, ws, error):
        self.info("mtaDevice._on_error()")
        self.error(error)
        pass

    def _on_close(self, ws):
        self.info("mtaDevice._on_close()")
        pass

    def sendMessage(self, message):
        """
        send message(utf-8 str) to MTA
        """
        self.info("mtaDevice.sendMessage(%s" % message[:40 if len(message) > 45 else len(message)] + '...)' if len(message) > 45 else ')')
        self._dstApl = "RENV"

        aplIdLength = bitstring.BitStream(int=len(self._dstApl), length=8)
        devIdLength = bitstring.BitStream(int=len(self._deviceName), length=8)
        payloadLength = bitstring.BitStream(int=len(message), length=32)
        aplId = bitstring.BitStream(bytes=self._dstApl, length=len(self._dstApl)*8)
        devId = bitstring.BitStream(bytes=self._deviceName, length=len(self._deviceName)*8)
        payload = bitstring.BitStream(bytes=message, length=len(message)*8)

        sendData = aplIdLength + devIdLength + payloadLength + aplId + devId + payload
        self._ws.send(sendData.bytes, websocket.ABNF.OPCODE_BINARY)

        pass

    def run_forever(self):
        """
        websocket connection start
        """
        self.info("mtaDevice.run_forever()")
        self._ws.run_forever()
        pass
