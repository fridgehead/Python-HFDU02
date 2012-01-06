import cv
import numpy as np
import pymorph as m
import mahotas
elem = np.array([[0,0,0],[0,1,0],[0,0,0]])

im = mahotas.imread("before.png")

im = im[:,:,0]

print "starting img process.. binarizing"
b1 = im > 205 #binarize
#remove single pixels
singpix = mahotas.morph.hitmiss(b1, elem)
b1 = (b1 - singpix) > 0


print "thinning"
b2 = m.thin(b1) #thin
print "pruning"
b3 = m.thin(b2, m.endpoints('homotopic'), 8)

#remove single pixels
singpix = mahotas.morph.hitmiss(b3, elem)
b3 = b3 - singpix

struct = np.ndarray((4,3,3))
struct[0,:,:] = [[1,0,1],[0,1,0],[0,1,0]]
for i in range(1, 4):
	print "gen %i structure.." % (i)
	struct[i,:,:] = np.rot90(struct[0],i)


struct = struct == 1
print "using struct for branch summing:"
print struct

b4 = np.zeros((301,398))
for x in range(1, b3.shape[0] -1):
	for y in range(1, b3.shape[1]-1):
		if (b3[x,y] == 1):
			for i in range(0,4):
				val = b3[x-1:x+2, y-1:y+2][struct[i]]
				if sum(val) == 4:
					print "Branch at %i %i with sum %i" % (x,y,sum(val))
					b4[x][y]=True



imgout = m.overlay(b1,b3,b4)
mahotas.imsave("lol.png", imgout)




