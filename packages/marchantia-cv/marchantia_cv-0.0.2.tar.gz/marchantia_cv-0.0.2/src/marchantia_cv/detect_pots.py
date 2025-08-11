#############################################
######     Detecting Tray and Pots     ######
#############################################

#Import packages
import cv2
import numpy as np
import matplotlib.pyplot as plt
import gc

def detect_layers(img_hsv, blur, kernel_size):

    img_blur = cv2.blur(img_hsv, (blur, blur))
    # print("Img blur shape: ", img_blur.shape)
    pixel_values = img_blur.reshape((-1, 3))
    # print("pixel values shape: ", pixel_values.shape)
    pixel_values = np.float32(pixel_values)

    # Set kmeans criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.2)
    k = kernel_size

    # Find centres - random centers is fastest (?)
    _, labels, centres = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    # print("labels shape: ", labels.shape)
    # print("centres: ", centres)

    # Segment image
    centres = np.uint8(centres)

    return centres, labels

def detect_tray(img):

    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    centres, labels = detect_layers(img_hsv, 100, 4)

    # Find segment with highest SATURATION - this is likely plant
    max_sat = max(centres[0:, 1])
    plant_centre = centres[centres[0:, 1] == max_sat]

    # Find segment with lowest VALUE that is not PLANT - this is likely tray

    min_val = min(centres[np.where(centres[0:, 1] != max_sat), 2][0])
    # print(min_val)
    tray_centre = centres[centres[0:, 2] == min_val]

    segmented_image = centres[labels.flatten()]
    # print("segmented image shape: ", segmented_image.shape)
    segmented_image = segmented_image.reshape(img.shape)

    # print("segmented image shape after reshape: ", segmented_image.shape)

    # select colour and create mask
    layer = segmented_image.copy()
    mask = cv2.inRange(layer, tray_centre, tray_centre)

    # apply mask to layer
    layer[mask == 0] = [0, 0, 0]

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Just draw largest contour
    max_contour = max(contours, key=cv2.contourArea)
    grey = cv2.cvtColor(layer, cv2.COLOR_BGR2GRAY)
    image_contours = np.zeros_like(grey)

    epsilon = 0.1 * cv2.arcLength(max_contour, True)
    approx = cv2.approxPolyDP(max_contour, epsilon, True)

    rect = cv2.minAreaRect(approx)
    box = cv2.boxPoints(rect)
    box = np.int32(box)
    cv2.drawContours(image_contours, [box], -1, 255, 20)
    # Get coordinates of non-zero pixels inside the filled contour
    # print(f"image_contours shape: {image_contours.shape}")

    ys, xs = np.where(image_contours == 255)
    # Get the smallest box in max contour
    left, right = xs.min(), xs.max()
    top, bottom = ys.min(), ys.max()

    x, y, w, h = left, bottom, right-left, bottom-top

    #Cleanup
    del labels, centres, segmented_image, layer, grey, image_contours
    del mask, contours, max_contour, approx
    plt.close('all')
    gc.collect()

    return x, y, w, h
