#!/usr/bin/env python



import unittest
import renv_device

class TestRenvDeviceInfo(unittest.TestCase):
    """test class of tashizan.py
    """
    
    def setUp(self):
        self._devId = "uuid-1234-5678-9012"
        self._devTypeId = "WEB.DEVICE.TEST_DEVICE"
        self._devName = "name-renv-device-name-for-test"
        self._rd = renv_device.RenvDevice(self._devTypeId, self._devId, self._devName)

    def test_givenNameIsEqualToDeviceInfoName(self):
        """
        """
        deviceInfo = self._rd.getDeviceInfo()
        self.assertEqual(self._devName, deviceInfo['deviceName'])

    def test_givenIdIsEqualToDeviceInfoName(self):
        """
        """
        deviceInfo = self._rd.getDeviceInfo()
        self.assertEqual(self._devId, deviceInfo['deviceId'])


class MyRenvDevice(renv_device.RenvDevice):
    def __init__(self, typeId, id, name):
        renv_device.RenvDevice.__init__(self, typeId, id, name)
        pass
    
    
    def onSetup(self):
        print 'onSetup is called'
        pass



class TestRenvDeviceInfo(unittest.TestCase):
    """test class of tashizan.py
    """

        
            
    def setUp(self):
        self._devId = "uuid-1234-5678-9012"
        self._devTypeId = "WEB.DEVICE.TEST_DEVICE"
        self._devName = "name-renv-device-name-for-test"
        self._rd = MyRenvDevice(self._devTypeId, self._devId, self._devName)

    def test_givenNameIsEqualToDeviceInfoName(self):
        """
        """
        deviceInfo = self._rd.getDeviceInfo()
        self.assertEqual(self._devName, deviceInfo['deviceName'])

    def test_givenIdIsEqualToDeviceInfoName(self):
        """
        """
        deviceInfo = self._rd.getDeviceInfo()
        self.assertEqual(self._devId, deviceInfo['deviceId'])




if __name__ == "__main__":
    unittest.main()
