#############################################
###  Putting together formatting scripts  ###
#############################################

#Import packages
import cv2
import numpy as np
import glob
import matplotlib.pyplot as plt
import os

#Import scripts
import rotate_img
import warp_img

# Point to photos directory
cwd = os.getcwd()
photos_dir = "{}/photos".format(cwd)

#Setup output directories
out_dir = "{}/out_test".format(cwd)
formatted_outdir = os.path.join(out_dir, "formatted")
if not os.path.exists(formatted_outdir):
    os.makedirs(formatted_outdir)
files_written = 0

#Get image filenames
images = []
for root, dirs, files in os.walk(photos_dir):
        for name in files:
            if name.upper().endswith(".JPG"):
                images.append(os.path.join(root, name))

assert len(images) > 0, "No images found in {}".format(photos_dir)
total_images = len(images)
print("Found {} images".format(total_images))

# Define scale card template - this is used for orienting images correctly
template = cv2.imread('./calibration/scalecard.jpeg', cv2.IMREAD_COLOR_BGR)
assert template is not None, "Scale card file could not be read, check with os.path.exists()"

#Calibrating camera to correct for distortion
mtx, dist = warp_img.calibrate_checker('./calibration/checker')
assert mtx.any() and dist.any(), "Calibration failed."
print("\nCalibration complete",mtx, dist)

# Rotate images
formatted_images = 0


for img_fname in images:
    for root, dirs, files in os.walk(formatted_outdir):
        formatted_name = img_fname.split("/")[-1]
        if not any(formatted_name in name for name in files):
            print("\rRotating image {}. {}/{}.".format(formatted_name, formatted_images+1, total_images))

            img = cv2.imread(img_fname, cv2.IMREAD_COLOR_BGR)
            rotated_img = rotate_img.rotate(img, template)

            #Undistort images
            print("Correcting image distortion")

            undistorted_img = warp_img.undistort(rotated_img, mtx, dist)

            fname_out = formatted_name.replace(".JPG", "_formatted.jpg")

            print(f"Writing {fname_out} to {formatted_outdir}. {files_written+1}/{total_images}")
            cv2.imwrite(os.path.join(formatted_outdir, fname_out), undistorted_img)
            files_written += 1
            formatted_images += 1
        else:
            print(f"Image {img_fname} already processed, found in {formatted_outdir}")
            continue
            formatted_images += 1

print("\nFormatting complete. {} images in {}.".format(formatted_images, formatted_outdir))






