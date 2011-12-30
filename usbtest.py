import usb
from PIL import Image

def ledOn(handle):
   handle.bulkWrite(1, [0x05,0x01], 150)

def ledOff(handle):
   handle.bulkWrite(1, [0x05,0x00], 150)

def capRead(handle):
   r = handle.bulkWrite(1, [0x00, 0x04])
   if r != 2:
      print "capread fail"
      return False

   resp = handle.bulkRead(1,4,200)
   if resp != (0,4,1,1):
      return False
   return True

def capGo(handle):
   r = handle.bulkWrite(1, [0x00, 0x01])
   if r != 2:
      print "capGo fail"
      return False
   resp = handle.bulkRead(1,4, 200)
   if resp != (0x00,0x01,0x01,0x01):
      print "capGo invalid ack"
      return False
   dat= handle.bulkRead(2,401*301 *6, 1000)

   return dat

def capEnd(handle):
   r = handle.bulkWrite(1, [0x00, 0x05])
   if r != 2:
      print "capEnd fail"
      return False
   resp = handle.bulkRead(1,4, 200)
   if resp != (0x00,0x05,0x01,0x01):
      print "capEnd invalid ack"
      print resp
      return False
   return True

def processData(data):
	print "starting sol search"
	#find the 0f 0f 0f 0f 00 00 0b 06 SOL marker
	l = 0
	im = Image.new("L", (301,398))
	buf = im.load()
	needle = (0x0f, 0x0f, 0x0f, 0x0f, 0x00, 0x00, 0x0b, 0x06)
	lc = 0
	imCount = 0
	for i in range (len(data)):
		if data[i : i + len(needle)] == needle:
					
			lc = lc + 1
			linenum = i + len(needle) + 1
			d = data[linenum  ] << 8 | data[linenum + 1] << 4 | data[linenum + 2]
			#print "found SOL marker for line: " , d , " - off: " + str(hex(i))
			b = 0
			for pix in range(0,796,2):
				buf[d - 1,b] = data[linenum  + 3 + pix] << 4 | data[linenum + pix + 4]
				b = b + 1
			if lc == 300:
				im.save("piss.jpg")
				return
busses = usb.busses()

i = 0
for bus in busses :
    for dev in bus.devices :
        if dev.idVendor == int("1162",16) :
            print "Found a likely Finger device: "
            print "\tBus = ", i
            print "\tProduct = ", dev.idProduct
            print "\tVendor = ", dev.idVendor
            print "\tDevice Version:", dev.deviceVersion
	    d = dev.open()
	    try:
                d.detachKernelDriver(0)
	    except:
	        print "failed to detach"
	    print "setting config 1"
	    d.setConfiguration(1)
	    print "claiming.."
	    d.claimInterface(0)
	    d.setAltInterface(1)
	    d.clearHalt(2)
            ledOn(d)
            ledOn(d)
	    capOk = capRead(d)
	    print "capread: " , capOk
	    if capOk != True:
	        print "capread bailout"
		exit(1)
	    dat = capGo(d)
	    if dat == False:
	       print "cap error"
	    print "Capgo ret: ", len(dat)
            #print d.bulkRead(2, 404*301*6)
            capOk = capEnd(d)
	    if capOk == False:
	        print "capEnd failed"
		exit(1)
	    print "capEnd ret: ", capOk
            ledOff(d)
            d.resetEndpoint(1) 
	    d.releaseInterface()
            
	    #do something with the data
	    processData(dat)
	    
#start of frame seems to be a block of 0xf

