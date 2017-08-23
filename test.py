import os, sys, traceback


import renv_device


host = "192.168.1.200:8080"


def main():
    rd = renv_device.RenvDevice(host)
    rd.run()

    
if __name__ == '__main__':
    main()

