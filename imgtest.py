import cv
import numpy as np
import pymorph as m
import mahotas

im = mahotas.imread("before.png")
im = im[:,:,0]
print "starting img process.. binarizing"
b1 = im > 150 #binarize
#b1 = m.dilate(b1, m.sedisk(1))
print "thinning"
b2 = m.thin(b1) #thin
print "pruning"
b3 = m.thin(b2, m.endpoints('homotopic'), 3)

imgout = m.overlay(b1,b3)
mahotas.imsave("lol.png", imgout)




