#############################################
###    Split image to n rows and n columns    ###
#############################################

#Import packages
import cv2
import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
import os
from plantcv import plantcv as pcv
import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) ### !!!

def split_pots(img, rows, cols):
    pots = {}

    h = img.shape[0]//rows
    w = img.shape[1]//cols
    pot_label = 0

    for i in range(rows):
        for j in range(cols):
            pot_label += 1
            y1, y2 = i * h, (i + 1) * h
            x1, x2 = j * w, (j + 1) * w
            rgb = cv2.cvtColor(img[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
            pots[pot_label] = img[y1:y2, x1:x2]
    return pots
