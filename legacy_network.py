# Samuel Caesar, Kate Liu, and Ichiro Miyasato (Team 7)
# 14 October 2024
# CST 311 Programming Assignment 4
# legacy_network.py

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from mininet.term import makeTerm
import time
import subprocess
subprocess.run(["sudo", "-E", "python3", "certificate_generation.py"])


def myNetwork():
    net = Mininet(topo=None, build=False)

    info( '*** Adding controller\n' )
    c0 = net.addController(name='c0', controller=Controller, protocol='tcp', port=6633)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info( '*** Add routers\n')
    r3 = net.addHost('r3', cls=Node, ip='10.0.1.254/24')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')
    r4 = net.addHost('r4', cls=Node)
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
    r5 = net.addHost('r5', cls=Node, ip='10.0.2.254/24')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.1/24', defaultRoute='via 10.0.1.254')
    h2 = net.addHost('h2', cls=Host, ip='10.0.1.2/24', defaultRoute='via 10.0.1.254')
    h3 = net.addHost('h3', cls=Host, ip='10.0.2.1/24', defaultRoute='via 10.0.2.254')
    h4 = net.addHost('h4', cls=Host, ip='10.0.2.2/24', defaultRoute='via 10.0.2.254')

    info( '*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)
    net.addLink(s1, r3)
    net.addLink(s2, r5)

    link1 = net.addLink(r3, r4)
    link2 = net.addLink(r4, r5)

    info( '*** Starting network\n')
    net.build()

    # Setting IP addresses explicitly
    link1.intf1.setIP('192.168.0.2/30')
    link1.intf2.setIP('192.168.0.1/30')
    link2.intf1.setIP('192.168.0.6/30')
    link2.intf2.setIP('192.168.0.5/30')

    # Adding static routes
    r3.cmd('ip route add 10.0.2.0/24 via 192.168.0.1')
    r3.cmd('ip route add 192.168.0.4/30 via 192.168.0.1')
    r4.cmd('ip route add 10.0.1.0/24 via 192.168.0.2')
    r4.cmd('ip route add 10.0.2.0/24 via 192.168.0.5')
    r5.cmd('ip route add 10.0.1.0/24 via 192.168.0.6')
    r5.cmd('ip route add 192.168.0.0/30 via 192.168.0.6')

    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()
    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    
    info( '*** Post configure switches and hosts\n')
    # We force sleeps here to ensure that the server script runs before all the client scripts.
    time.sleep(1)
    # Start the chat server on h4
    makeTerm(h4, title='Node', term='xterm', display=None, cmd='python3 tpa4_chat_server.py; bash')
    time.sleep(1)
    # Start chat clients on h1, h2, and h3
    makeTerm(h1, title='Node', term='xterm', display=None, cmd='python3 tpa4_chat_client.py; bash')
    time.sleep(1)
    makeTerm(h2, title='Node', term='xterm', display=None, cmd='python3 tpa4_chat_client.py; bash')
    time.sleep(1)
    makeTerm(h3, title='Node', term='xterm', display=None, cmd='python3 tpa4_chat_client.py; bash')


    # CLI
    CLI(net)
    net.stop()
    net.stopXterms()

if __name__ == '__main__':
    
    setLogLevel( 'info' )
    myNetwork()
