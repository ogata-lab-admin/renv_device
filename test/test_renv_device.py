#!/usr/bin/env python



import unittest
import renv_device

class TestRenvDevice(unittest.TestCase):
    """test class of tashizan.py
    """

    def test_givenNameIsEqualToDeviceInfoName(self):
        """
        """
        devId = "dev"
        uuid = "uuid"
        name = "name_renv_device_id_for_test"
        rd = renv_device.RenvDevice(devId, uuid, name)

        deviceInfo = rd.getDeviceInfo()
        self.assertEqual(name, deviceInfo['deviceName'])

if __name__ == "__main__":
    unittest.main()
