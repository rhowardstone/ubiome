#https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-pythonhttps://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python

import numpy as np
import PIL
from PIL import Image
import sys


if __name__ == "__main__":
	if len(sys.argv)<5:
		print("Error - usage:\n >>> python Combine_images.py [Out_fname.png] [0/1 horizontal/vertical] [Img1.png] [Img2.png] ...\n")
		exit()
	out_fname, ori = sys.argv[1:3]
	list_im = sys.argv[3:]
	
	imgs    = [ Image.open(i) for i in list_im ]
	# pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
	min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
	
	if ori == '0':
		imgs_comb = np.hstack([i.resize(min_shape) for i in imgs])
	elif ori == '1':
		# for a vertical stacking it is simple: use vstack
		imgs_comb = np.vstack([i.resize(min_shape) for i in imgs])
	else:
		print("Error -", ori, "not recognized. Options: 0, or 1.\n")
		exit()
	imgs_comb = Image.fromarray( imgs_comb)
	imgs_comb.save(out_fname)
