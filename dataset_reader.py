import numpy as np
import os
from os import listdir
from os.path import isfile, join
import cv2
import scipy
import itertools
import pickle
import matplotlib.pyplot as plt

ROOTDIR = "./Img_minibatch/img/MEN/Denim"

class DataLoader:
    images = None #(?,256,256,3)
    heatmaps = None #(?,256,256,18)
    morphologicals = None #(?,256,256)
    pairs=[]
    groupsofIndices = []


    def __init__(self):
        print("Initializing DeepFashion Dataset Loader...")
        self._read_images()

    def _read_images(self):
        self.images = self._getData()

    def _getData(self):
        for root, dirs, files in os.walk(ROOTDIR, topdown=True):
            # same directory
            code2index = {} # code is 01/02/03 etc. Index is 0 through 50000
            for file in files:
                fulldir = root + '/' + file
                if not "flat" in file:
                    img = cv2.imread(fulldir)
                    if img is not None:
                        # perform left-right flip
                        img = np.expand_dims(img,axis=0)
                        flippedImg = np.flip(img, axis=2)
                        # process the keypoint thing
                        heatmap = np.zeros([256,256,18]) # (of original image)
                        mapofAllPoints = np.zeros([256,256])

                        # process the stored keypoints
                        with open (fulldir+'keypoints','rb') as kpfile:
                            keypoints = pickle.load(kpfile)
                            for i in range(len(keypoints)):
                                keypoint = keypoints[i]
                                if len(keypoint)!=0:    # a non-empty keypoint is a list consists of one and only one tuple.
                                    heatmap[:,:,i] = cv2.circle(np.zeros([256,256]), (keypoint[0][0], keypoint[0][1]), 4,255, -1)
                                    cv2.circle(mapofAllPoints, (keypoint[0][0], keypoint[0][1]), 4,255, -1)
                                    pass

                                


                        heatmap = np.expand_dims(heatmap, axis=0)
                        heatmap_flippedimg = np.flip(heatmap, axis=2)

                        kernel = np.asarray([
                            [0, 0, 1, 0, 0],
                            [0, 1, 1, 1, 0],
                            [1, 1, 1, 1, 1],
                            [0, 1, 1, 1, 0],
                            [0, 0, 1, 0, 0]], dtype=np.uint8)
                        print(kernel)
                        dilatedMapofAllPoints = cv2.dilate(mapofAllPoints, kernel, iterations=9)
                        dilatedMapofAllPoints_flipped = np.flip(dilatedMapofAllPoints,axis=1)


                        # add both images and heatmaps to the their respective grand ndarrays
                        if self.images is None:
                            self.images = np.concatenate([img, flippedImg],axis=0)
                            self.heatmaps = np.concatenate([heatmap, heatmap_flippedimg],axis=0)
                        else:
                            self.images = np.concatenate([self.images,img,flippedImg],axis=0)
                            self.heatmaps = np.concatenate([self.heatmaps,heatmap,heatmap_flippedimg],axis=0)
                            pass
                        # code means "which variation of this cloth". Only clothes with the same code are deemed a PAIR.
                        code = file[0:2]
                        if code in code2index:
                            code2index[code].append(len(self.images)-2)
                            code2index[code].append(len(self.images)-1)
                        else:
                            code2index[code] = [len(self.images)-2,len(self.images)-1]
                        pass



        for k,v in code2index.items():
            self.groupsofIndices.append(v)

        # Generate pairs
        for group in self.groupsofIndices:
            self.pairs.append(list(itertools.combinations(group,2)))
        self.pairs = list(itertools.chain.from_iterable(self.pairs))

        print(self.pairs)
        pass

    def next_batch(self, batch_size):
        pass

loader = DataLoader()