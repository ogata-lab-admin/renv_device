#!/usr/bin/env python



import unittest
import renv_device



class MyRenvDevice(renv_device.RenvDevice):
    def __init__(self, typeId, id, name):
        renv_device.RenvDevice.__init__(self, typeId, id, name)
        pass
    
    
    def onSetup(self):
        """
        This function is called at first.
        """
        print 'onSetup is called'
        pass


    def onEcho(self, value):
        """
        This function echoes
        
        @param {String} value Echo back value [echo1 : Echo Data 1, echo2 : Echo Data 2]
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
        self.assertEqual(self._devId, deviceInfo['deviceId'])




if __name__ == "__main__":
    unittest.main()
