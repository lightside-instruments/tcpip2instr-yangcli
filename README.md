## VXI11 TCP/IP to yangcli gateway
This piece of software implements VXI11 server for configuration of NETCONF/YANG devices
through simple command line interface derived from the YANG model of the device.
The funcionality is comparable to a Ethernet-to-GPIB bridge.
It uses coburnw's python-vxi11-server and the yuma123 yangcli python bindings.
Only read and write methods are supported.

# Installation
Instructions for Debian-like system:

```
sudo apt-get install rpcbind
sudo systemctl start rpcbind
sudo systemctl enable rpcbind

git clone https://github.com/coburnw/python-vxi11-server.git
git clone https://github.com/lightside-instruments/tcpip2instr-yangcli.git
cd tcpip2instr-yangcli
python3 tcpip2instr-yangcli.py networks.xml
```

# Usage
After running this application, a VXI11 server listens on the device for incoming connections.
Incoming connection requests to device names of the form "gpib,foo" are mapped to NETCONF connection
to node named foo with address and password/keys specified in the networks.xml.

A simple example using python-vxi11 could look like this:

```
import vxi11

instr = vxi11.Instrument("TCPIP::localhost::gpib,foo::INSTR")

instr.write("replace /system -- contact='hello'")
instr.write("commit")
print(instr.read())
```
