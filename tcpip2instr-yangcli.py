import sys
import os
import signal
import time
import logging

from lxml import etree
import math
import subprocess
import argparse
import tntapi
import yangrpc
from yangcli.yangcli import yangcli

conns=None
yconns=None

namespaces={"nc":"urn:ietf:params:xml:ns:netconf:base:1.0",
	"nd":"urn:ietf:params:xml:ns:yang:ietf-network",
	"nt":"urn:ietf:params:xml:ns:yang:ietf-network-topology",
	"if":"urn:ietf:params:xml:ns:yang:ietf-interfaces",
	"tg":"urn:ietf:params:xml:ns:yang:ietf-traffic-generator",
	"ta":"urn:ietf:params:xml:ns:yang:ietf-traffic-analyzer"
}

sys.path.append(os.path.abspath('../python-vxi11-server/'))
import vxi11_server as Vxi11

class YangcliDevice(Vxi11.InstrumentDevice):
    READ_BLOCK_SIZE = 16384
    def __init__(self, device_name, device_lock):
        super(YangcliDevice, self).__init__(device_name, device_lock)

        self.name = device_name.split(",")[1]
        self.conn = conns[self.name]
        self.yconn = yconns[self.name]

        
    def device_write(self, opaque_data, flags, io_timeout):
        # TODO: handle flags/timeout
        error = Vxi11.Error.NO_ERROR
        print(self.yconn)
        print(opaque_data)
        try:
            self.last_result = yangcli(self.yconn, opaque_data.decode())
        except Exception as e:
            error = Vxi11.Error.IO_ERROR
            print(e)
        print("Returning:")
        print(error)
        return error
    
    def device_read(self, request_size, term_char, flags, io_timeout):
        # TODO handle request_size/term_char/flags/timeout
        error = Vxi11.Error.NO_ERROR
        reason = 4  # TODO: should be Vxi11.RX_END
        result = "OK"
        return error, reason, bytearray(result)

def signal_handler(signal, frame):
    logger.info('Handling Ctrl+C!')
    instr_server.close()
    sys.exit(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to exit')
    logger.info('starting time_device')
    
    # create a server, attach a device, and start a thread to listen for requests
    instr_server = Vxi11.InstrumentServer()


    tree=etree.parse(sys.argv[1])
    network = tree.xpath('/nc:config/nd:networks/nd:network', namespaces=namespaces)[0]


    logger.info('Connecting to NETCONF devices raw ...')
    conns = tntapi.network_connect(network)

    logger.info('Connecting to NETCONF devices yangcli ...')
    yconns = tntapi.network_connect_yangrpc(network)

    logger.info('Done.')

# yangcli
    for yconn in yconns:
        instr_server.add_device_handler(YangcliDevice, "gpib,%s" % (yconn))

    instr_server.listen()

    # sleep (or do foreground work) while the Instrument threads do their job
    while True:
        time.sleep(1)

