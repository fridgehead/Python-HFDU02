import cv
import usb
from PIL import Image
import pymorph as m
import numpy as np
import mahotas

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
   dat= handle.bulkRead(2,301*398 *9, 2500)

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

def getRawImage(data):
	print "starting sol search"
	#find the 0f 0f 0f 0f 00 00 0b 06 SOL marker
	l = 0
	im = Image.new("L", (301,398))
	img = np.zeros([301,398], dtype=np.uint8)
	buf = im.load()
	needle = (0x0f, 0x0f, 0x0f, 0x0f, 0x00, 0x00, 0x0b, 0x06)
	imCount = 0
	retVal = None
	lc = 0
	for i in range (len(data)):
		linenum = 0
		if data[i : i + len(needle)] == needle:
					
			lc = lc + 1
			linenum = i + len(needle) + 1
			d = data[linenum  ] << 8 | data[linenum + 1] << 4 | data[linenum + 2]
			#print "found SOL marker for line: " , d , " - off: " + str(hex(i))
			b = 0
			for pix in range(0,796,2):
				try:
					buf[d - 1,b] = data[linenum  + 3 + pix] << 4 | data[linenum + pix + 4]
					img[d-1,b] = buf[d - 1,b]
					b = b + 1
				except:
					print "EOD"
			if lc == 300:
				lc = 0
				#img[0:98, :] = 0
				print "..found image"
				im.save("piss" + str(imCount) + ".jpg")
				imCount += 1
				retVal = img
	print 'return the last succesful frame to let the AGC warm up'
	return retVal
#binarize image
#thin image
#return for feature matching later
def processImage(im):
	imb = m.overlay(im)
	mahotas.imsave("before.png",imb)
	print "starting img process.. binarizing"
	b1 = im > 100 #binarize
	print "thinnning"
	b2 = m.thin(b1) #thin
	print "pruning"
	b3 = m.thin(b2, m.endpoints('homotopic'), 10)

	imgout = m.overlay(b3)
	mahotas.imsave("lol.png", imgout)


#thin the binary image
def thinImage(cvim):
	pass	


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
	    im = getRawImage(dat)
            im2 = processImage(im) 

	    
#start of frame seems to be a block of 0xf

