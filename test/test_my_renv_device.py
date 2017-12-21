#!/usr/bin/env python

import unittest, json
from renv_device import RenvDevice, eventHandler, event


class MyRenvDevice(RenvDevice):
    def __init__(self, typeId, id, name):
        RenvDevice.__init__(self, typeId, id, name)
        self._msg_buffer = []
        pass
    
    @eventHandler
    def onSetup(self):
        """
        This function is called at first.
        """
        print 'onSetup is called'
        pass

    @eventHandler
    def onEcho(self, value):
        """
        This function echoes the given value
        @param {String} value Echo back value [echo1 : Echo Data 1 | echo2 : Echo Data 2]
        """
        self._msg_buffer.append('MyRenvDevice.onEcho(' + value + ') called.')
        pass

    @event
    def sendEchoBack(self, value):
        """
        This function send back the echo information.
        """
        self._msg_buffer.append('MyRenvDevice.onEchoBack(' + value + ') called.')
        return value
        
    @eventHandler
    def onTestMessage(self, value):
        """
        This is test function.
        @param {Int} value data test value.
        """
        print value
        pass

class TestMyRenvDeviceInfo(unittest.TestCase):
    """test class of tashizan.py
    """

        
            
    def setUp(self):
        self._devId = "uuid-1234-5678-9012"
        self._devTypeId = "WEB.DEVICE.TEST_DEVICE"
        self._devName = "name-renv-device-name-for-test"
        self._rd = MyRenvDevice(self._devTypeId, self._devId, self._devName)

    def test_givenIdIsEqualToDeviceInfoName(self):
        """
        """
        deviceInfo = self._rd.getDeviceInfo()
        #print deviceInfo
        self.assertEqual(self._devId, deviceInfo['deviceId'])
        self.assertEqual(self._devTypeId, deviceInfo['deviceTypeId'])
        self.assertEqual(self._devName, deviceInfo['deviceName'])
                         
        capabilities = deviceInfo['capabilityList']
        foundSetup = False
        foundEcho = False
        foundEchoBack = False
        for c in capabilities:
            if c['eventName'] == 'Setup':
                foundSetup = True
                self.assertEqual(c['eventType'], "In")

            if c['eventName'] == 'Echo':
                foundEcho = True
                self.assertEqual(c['eventType'], "In")

            if c['eventName'] == 'EchoBack':
                foundEchoBack = True
                self.assertEqual(c['eventType'], "Out")
            pass
        self.assertTrue(foundSetup)
        self.assertTrue(foundEcho)
        self.assertTrue(foundEchoBack)
            
        #print deviceInfo


    def test_dispachMessage(self):
        self._rd._dispatch_message(json.dumps({
                "eventName": "Echo",
                "eventParam" : {
                    "value" : {"val" : "test_echo_value01",} }}))




if __name__ == "__main__":
    unittest.main()
