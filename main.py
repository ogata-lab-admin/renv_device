import os, sys, traceback
from renv_device import RenvDevice, eventHandler, event

host = "localhost:8080"


class MyRenvDevice(RenvDevice):
    def __init__(self):
        RenvDevice.__init__(self, 'WEB.DEVICE.TESTER', 'ogata-tester')
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
        print value
        self._msg_buffer.append('MyRenvDevice.onEcho(' + value + ') called.')
        pass



def main():
    rd = MyRenvDevice()
    rd.connect(host)
    rd.run_forever()

    
if __name__ == '__main__':
    main()

