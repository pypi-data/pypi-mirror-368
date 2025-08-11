########################################
###      Correct Image Distortion    ###
########################################

#Import packages
import cv2
import numpy as np
import glob
import matplotlib.pyplot as plt

### WARP ###
#Undistorts image by calibration with checkerboard

# From https://docs.opencv2.org/4.x/dc/dbb/tutorial_py_calibration.html and https://csundergrad.science.uoit.ca/courses/cv-notes/notebooks/02-camera-calibration.html
def calibrate_checker(checker_dir):
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((9*10,3), np.float32)
    objp[:,:2] = np.mgrid[0:9,0:10].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    images = glob.glob('{}/*.JPG'.format(checker_dir))
    #print(images)

    print("Calibrating camera distortion from %d images." % len(images))

    # Read greyscale chessboards
    for filename in images:
        checker = cv2.imread(filename)
        assert checker is not None, "file could not be read, check with os.path.exists()"
        checker_grey = cv2.cvtColor(checker, cv2.COLOR_BGR2GRAY)
        (thresh, checker_bw) = cv2.threshold(checker_grey, 127, 255, cv2.THRESH_BINARY)

        ret, corners = cv2.findChessboardCorners(checker_grey, (9,10), None)

        if ret:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(checker_grey, corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)
            print("\r{}/{} complete".format(len(imgpoints), len(images)), end="")

            # Draw corners
            #cv2.drawChessboardCorners(checker, (9,10), corners2, ret)

            #corners2 = np.squeeze(corners2) # Get rid of extraneous singleton dimension

            # # Add circles to img at each corner identified
            # for corner in corners2:
            #     coord = (int(corner[0]), int(corner[1]))
            #     cv2.circle(img=checker, center=coord, radius=25, color=(255, 0, 0), thickness=100)
            #
            # plt.imshow(checker)
            # plt.show()
    # Calibrate camera
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, checker_grey.shape[::-1], None, None)

    return mtx, dist

#Undistort single image
def undistort(img, mtx, dist):
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 0, (w, h))
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

    return dst