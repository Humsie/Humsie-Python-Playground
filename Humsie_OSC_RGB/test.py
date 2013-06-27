#!/usr/bin/python

from OSC import *;
import time;

clients = {};



def handler_toggle(addr, tags, data, client_address):
	c = OSCClient()
	c.connect((client_address[0], 9000))
	#c.connect(client_address)	# connect back to the client
	inforeq = OSCMessage(addr.replace("toggle", "fader"))
	inforeq.append(data);
	print inforeq
	c.send(inforeq);

def handle_color(addr, tags, data, client_address):
    addrparts = addr.strip('/').split('/');
    
    print "Setting color %s to value %f" % ( addrparts[1], data[0] );
    
def handle_preselect(addr, tags, data, client_address):
	addrparts = addr.strip('/').split('/');
	try:
		clients[addrparts[1]].clearData();
	except KeyError:
		clients[addrparts[1]] = OSCClient();
		clients[addrparts[1]].connect((client_address[0], 9000))
	except AttributeError:
		i = 0;
		# do nothing
			
	response = OSCMessage(addr)
	response.append(data[0]);
	clients[addrparts[1]].send(response);

	if data[0] == 1.0:
		colors = {"1":"red", "2":"green", "3":"blue"};
		presets = {"1":0, "2":0.5, "3":1};

		response = OSCMessage("/1/%s" % colors[addrparts[3]])
		response.append(presets[addrparts[2]]);
		print response
		clients[addrparts[1]].send(response);
		
		
	
	print "Preselect %s.%s has been clicked to value %f" % ( addrparts[2], addrparts[3], data[0] );


def handler_toggleX(addr, tags, data, client_address):

	time.sleep(0.5);
	c = OSCClient()
	c.connect((client_address[0], 9000))
	#c.connect(client_address)	# connect back to the client
	inforeq = OSCMessage(addr)
	inforeq.append(1);
		
	print inforeq
	c.send(inforeq);

def handler(addr, tags, data, client_address):
#	c = OSCClient()
#	c.connect((client_address[0], 9000))
#	inforeq = OSCMessage(addr)
#	inforeq.append(0);
#	c.send(inforeq);


	print "adress %s %s %s %s" % (addr, tags, data, client_address);
	return

	

listen_address = ('0.0.0.0', 8000);

c = OSCClient()
c.connect(listen_address)	# connect back to our OSCServer

s = ThreadingOSCServer(listen_address, None, 0)

print s

#s.addDefaultHandlers()
s.addMsgHandler('default', handler);
s.addMsgHandler('/1/toggle1', handler_toggle);
s.addMsgHandler('/1/toggle2', handler_toggle);

for color in ("red", "green", "blue"):
	s.addMsgHandler("/1/%s" % color, handle_color);

for x in ("1", "2", "3"):
	for y in ("1", "2", "3"):
		s.addMsgHandler("/1/preselect/%s/%s" % (x, y), handle_preselect);



print "Registered Callback-functions:"
for addr in s.getOSCAddressSpace():
	print addr

print "\nStarting OSCServer. Use ctrl-C to quit."
st = threading.Thread(target=s.serve_forever)
st.start()

try:
	while True:
		time.sleep(30)

except KeyboardInterrupt:
	print "\nClosing OSCServer."
	s.close()
	print "Waiting for Server-thread to finish"
	st.join()
	print "Closing OSCClient"
	c.close()
#	print "Done"