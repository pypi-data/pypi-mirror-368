##################################
###      Image Orientation     ###
##################################

#Import packages
import cv2
import numpy as np

### ROTATE ###
#Finds scale card and rotates so that it is at the bottom of the image

def rotate(img, template):

    img = img.copy()
    img_h, img_w = img.shape[:2]
    template_h, template_w = template.shape[:2]
    w_threshold = min(img_w, img_h)*0.75
    h_threshold = max(img_h, img_w)*0.25
    # print("Scale card expected near ({}, {})". format(w_threshold, h_threshold))

    #print("width:",img_w, "height:",img_h)

    method = getattr(cv2, "TM_CCOEFF_NORMED")

    no_match = True
    _minVal = _maxVal = minLoc = maxLoc = None
    rotations = 0
    best_conf = 0

    while no_match:
        #Any landscape images are flipped to portrait
        if img_w > img_h:
            print("Width:", img_w, "Height:", img_h)
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            img_h, img_w = img.shape[:2]
            print("Flipped so width:",img_w, "height:",img_h)

        #Look for scale card
        res = cv2.matchTemplate(img,template,method)
        _minVal, _maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)
        match_conf = round(np.amax(res), 3)
        if match_conf > best_conf:
            best_conf = match_conf
            best_rotation = rotations
        #print(maxLoc)

        #Match is correct if scale card correctly located in top right of image
        top_right = (maxLoc[0]+template_w, maxLoc[1])
        if top_right[0] > w_threshold and top_right[1] < h_threshold:
            print("\rMatch found. Confidence: {}.".format(match_conf))
            no_match = False
            continue

        print(f"Match only", match_conf, "confident. Rotating...")
        img = cv2.rotate(img, cv2.ROTATE_180)
        rotations += 1

        if rotations >= 2:
            print("Rotations exceeded. Rotating again {} times". format(best_rotation))
            for i in range(best_rotation):
                img = cv2.rotate(img, cv2.ROTATE_180)
            no_match = False
            continue

        continue

    print(f"Top right corner of scale card found at {top_right}.")
    print(f"Image width: ", img_w, 'image height: ', img_h)

    top_left = maxLoc
    bottom_right = top_left[0]+template_w, top_left[1]+template_h

    return img #, top_left, bottom_right

### TEST
# import matplotlib.pyplot as plt
#
# template = cv2.imread('./calibration/scalecard.jpeg', cv2.IMREAD_COLOR_BGR)
# img = cv2.imread("/Users/piphill/Desktop/Marchantia/phill_gxe_pheno/photos/20250520/2025_05_2001.JPG", cv2.IMREAD_COLOR_BGR)
# canvas, top_left, bottom_right = rotate(img, template)
# print(top_left, bottom_right)
# cv2.rectangle(canvas, top_left, bottom_right, 255, 80)
#
# plt.figure(figsize=[8,8])
# plt.imshow(canvas)
# plt.title("Scalecard Used to Orient Image")
# plt.show()

