#!/usr/bin/env python
#encoding: utf-8 

import os, sys, traceback, logging

from logging import getLogger
from renv_device import RenvDevice, actionHandler, event

#host = "localhost:8080"
#host = "192.168.1.24:8080"
#host = "192.168.128.157:8080"
host = "192.168.170.237:8080"
use_mta = False
mta_host = "192.168.128.130:8001"
key="xKV927K9MuAmkj+N3qgADjaZ+BkABc3BUbtDLbEIldk="
logging.basicConfig(filename='example.log',level=logging.DEBUG, format='%(levelname)s:%(asctime)s %(message)s')
logger = getLogger(__name__)

if use_mta:
    host = mta_host

class MyRenvDevice(RenvDevice):
    def __init__(self):
        """
        """

        # RenvDevice.__init__(self, 'WEB.DEVICE.TESTER', 'ogata-tester', use_mta=False)
        RenvDevice.__init__(self, 'WEB.DEVICE.NME_TESTER', 'ogata-tester', use_mta=use_mta, deviceName="NME_TESTER", logger=logger, deviceAuthenticationKey=key)
        self._msg_buffer = []
        pass
    
    @actionHandler
    def onSetup(self):
        """
        この関数はデバイス側コンソールに文字列を出力するのみです
        """
        print 'onSetup is called'
        pass

    @actionHandler
    def onEcho(self, value):
        """
        この関数は入力valueをコンソールに出力します

        :param String value: エコーする値 [echo1 : Echo Data 1 | echo2 : Echo Data 2]
        """
        print value
        self._msg_buffer.append('MyRenvDevice.onEcho(' + value + ') called.')
        pass



def main():
    rd = MyRenvDevice()
    rd.connect(host)
    rd.run_forever()

    
if __name__ == '__main__':
    main()

