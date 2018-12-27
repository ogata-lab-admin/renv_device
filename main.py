#!/usr/bin/env python
# -encoding: utf-8 

import os, sys, traceback, logging, codecs, argparse

from logging import getLogger

from renv_device import RenvDevice, actionHandler, event
# sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

#host = "localhost:8080"
host = "renv.xfarm.jp:8443"
use_mta = False
mta_host = "192.168.128.130:8001"


logging.basicConfig(filename='example.log',level=logging.DEBUG, format='%(levelname)s:%(asctime)s %(message)s')
logger = getLogger(__name__)

if use_mta:
    host = mta_host

class MyRenvDevice(RenvDevice):
    def __init__(self, filename=None):
        """
        """

        # RenvDevice.__init__(self, 'WEB.DEVICE.TESTER', 'ogata-tester', use_mta=False)
        RenvDevice.__init__(self, filename=filename, logger=logger)
        self._msg_buffer = []

        paramInfo = self.buildParamInfo('arg1', 'String', 'Test argument')
        self.addCustomActionHandler('Echo2', 'Test Command', [paramInfo], self._handler)
        print self.deviceInfoText
        
        self.updateDeviceInfo()

        print '-'*20
        print self.deviceInfoText
        pass

    def _handler(self, arg1):
        print ('MyRenvDevice._handler called')
        print (arg1)
    
    def hoge_onSetup(self):
        """
        この関数はデバイス側コンソールに文字列を出力するのみです
        """
        print 'onSetup is called'
        pass

    @actionHandler
    def onEcho(self, value):
        """
        Show value to console

        :param String value: Echo value [echo1 : Echo Data 1 | echo2 : Echo Data 2]
        """
        print value
        self._msg_buffer.append('MyRenvDevice.onEcho(' + value + ') called.')
        pass



def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--filename', help='config file path', type=str, dest='filename', default=None)
        parser.add_argument('-o', '--o', help='capability description output file path', type=str, dest='output', default=None)
        args = parser.parse_args()
        
        rd = MyRenvDevice(filename=args.filename)
        
        with open(args.output, 'w') as f:
            f.write(rd.getCapabilityStr())
        rd.connect(host)
        rd.run_forever()
    except:
        traceback.print_exc()
    
    
if __name__ == '__main__':
    main()

