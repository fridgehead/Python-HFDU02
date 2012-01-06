import cv
import numpy as np
import pymorph as m
import mahotas

class FingerProcess:
	def process(self,im):
		#single pixel restructure element
		elem = np.array([[0,0,0],[0,1,0],[0,0,0]])

		print "starting img process.. binarizing"
		b1 = im > 205 #binarize
		print "removing single pixels"
		#remove single pixels
		singpix = mahotas.morph.hitmiss(b1, elem)
		b1 = (b1 - singpix) > 0
		print "closing holes"
		b1 = m.close_holes(b1)

		print "thinning"
		#b2 = m.thin(b1) #thin
		b2 = self.shitthin(b1) #thin
		print "pruning"
		b3 = m.thin(b2, m.endpoints('homotopic'), 8)

		#remove single pixels
		singpix = mahotas.morph.hitmiss(b3, elem)
		b3 = b3 - singpix
		b3 = b3 >0
		struct = np.ndarray((4,3,3), dtype=np.uint8)
		struct[0,:,:] = [[1,2,1],[0,1,0],[0,1,0]]
		for i in range(1, 4):
			print "gen %i structure.." % (i)
			struct[i,:,:] = np.rot90(struct[0],i)


		#struct = struct == 1
		print "using struct for branch summing:"
		print struct

		b4 = np.zeros((301,398), dtype=bool)
		
		for i in range(0,4):
			b4 = b4 | mahotas.morph.hitmiss(b3, struct[i])		
		b4 = b4 > 0

		imgout = m.overlay(b1,b2,b4)
		mahotas.imsave("thresh.png", imgout)
		return b4

	def shitthin(self, img):
		#shit thinning
		structleft = np.ndarray((4,3,3), dtype=np.uint8)
		structleft[0,:,:] = [[0,0,0],[2,1,2],[1,1,1]]
		for i in range(1, 4):
			structleft[i,:,:] = np.rot90(structleft[0],i)

		structright = np.ndarray((4,3,3), dtype=np.uint8)
		structright[0,:,:] = [[2,0,0],[1,1,0],[2,1,2]]
		for i in range(1, 4):
			structright[i,:,:] = np.rot90(structright[0],i)


		#run left, then right, then rotate and do the same. Keep this up until there are no more changes to the image
		lastFrame = img.astype(bool)  
		b =  np.copy(img).astype(bool)  
		ct = 0
		while(True):
			print "thinning iteration %i" % (ct)
			
			for ele in range(0,4):
				b = b | mahotas.morph.hitmiss(b, structleft[ele])

				b = b | mahotas.morph.hitmiss(b, structright[ele])
			print (np.all(lastFrame ==  b))
			if np.all(lastFrame ==  b) == True :
				break
			lastFrame = np.copy(b).astype(bool)
			ct += 1
		return lastFrame > 0

	def kmeans(self, img, maxiter):
		X = img
		thresh = X.mean()
		for iter in range(maxiter):
			thresh = (X[X<thresh].mean() + X[X>=thresh].mean())/2.0
			X[X<thresh] = 0
			X[X>=thresh] = 255
		return X == 255

if __name__ == "__main__":

	im = mahotas.imread("before.png")

	im = im[:,:,0]
	f = FingerProcess()
	b4 = f.process(im)
	imgout = m.overlay(im,b4)
	mahotas.imsave("lol.png", imgout)
