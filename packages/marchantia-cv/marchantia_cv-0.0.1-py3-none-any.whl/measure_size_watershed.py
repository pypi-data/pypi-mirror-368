#############################################
###    Measuring Marchantia Plant Size    ###
#############################################
import os

#Import packages
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from plantcv import plantcv as pcv

import re
import psutil
import gc
import datetime

import split_pots, detect_pots


#Cleanup function
def log_memory(note=""):
    mem = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    # print(f"[MEMORY] {note}: {mem:.2f} MB")

def log_failure(log_path, img_name, reason):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not os.path.exists(log_path):
        with open(log_path, 'w') as f:
            f.write(f"{datetime.datetime.now()} - Error log created\n"
                    f"{datetime.datetime.now()} - Image {img_name}: {reason}\n")
    else:
        with open(log_path, 'a') as f:
            f.write(f"{datetime.datetime.now()} - Image {img_name}: {reason}\n")

def process_image(img, now, outdirs):

    pcv.params.debug = None
    pcv.params.verbose = False

    # Initialise output

    size_out_fname = os.path.join(outdirs['size_out'], f"plant_size_{now}.csv")
    log_path = os.path.join(outdirs['size_out'], "failed_images.log")

    observations = {}
    entries = ['date', 'box', 'position', 'height', 'width', 'area', 'convex_hull_area']
    for entry in entries:
        observations[entry] = []

    img, path, fname = pcv.readimage(filename=img, mode="rgb")
    sample_label = fname.replace("_formatted.jpg", "")
    rec_date = re.sub(r'[^a-zA-Z0-9]', '', sample_label)[:-2]
    boxnum = sample_label[-2:]

    box_img_out = os.path.join(outdirs['img_out'], rec_date, boxnum)

    os.makedirs(box_img_out, exist_ok=True)

    # print(f"\n{sample_label}")

    # Down sample image
    img = cv2.pyrDown(img)

    # Crop image to tray
    # Define rows and columns of plants
    nrows = 4
    ncols = 3
    npots = nrows * ncols

    try:
        x, y, w, h = detect_pots.detect_tray(img)
    except Exception as e:
        log_failure(log_path, sample_label, f"Failed to segment tray. [ERROR]: {e} ")
        return sample_label, True

    # Detect the color card, create a matrix of color chip values, and perform linear color correction.
    img_cc = pcv.transform.auto_correct_color(rgb_img=img, label=sample_label)
    # Save chip size measurements, value is stored in outputs.metadata
    avg_chip_size = pcv.outputs.metadata['median_color_chip_size']['value'][0]

    # print("Colour chip area: {}\t"
    #       "Colour chip width: {}\t"
    #       "Colour chip height: {}".format(avg_chip_size, avg_chip_w, avg_chip_h))
    scale_factor = np.sqrt(138 / avg_chip_size)  # Estimated scale in mm

    img_cc_tray = img_cc[y - h:y, x:x + w]

    fname_crop = os.path.join(outdirs["crop_out"], sample_label + "_tray.jpg")
    cv2.imwrite(fname_crop, img_cc_tray)
    # print(f"Saved cropped image as {sample_label + "_tray.jpg"}")

    retry = 0
    while img_cc_tray is None or len(img_cc_tray.shape) != 3 or img_cc_tray.shape[2] != 3 and retry < 3:
        path = fname_crop
        img_cc_tray = cv2.imread(path)
        retry += 1
    if img_cc_tray is None or len(img_cc_tray.shape) != 3 or img_cc_tray.shape[2] != 3:
        log_failure(log_path, sample_label, f"Image read incorrectly after {retry} attempts.")
        return sample_label, True  # if the image is broken or greyscale, try again 3 times then skip this image and go to the next one

    ## SPLIT POTS ###
    pots = split_pots.split_pots(img_cc_tray, nrows, ncols)

    ### MASK GREEN ###

    pot_things = {}
    plot_ix_list = [i for i in range(1, npots * 4 + 1, 4)]
    plt.figure(figsize=(12, 36))

    for position, pot_img in pots.items():
        if pot_img is None or len(pot_img.shape) != 3 or pot_img.shape[2] != 3:
            log_failure(log_path, sample_label, f"{sample_label} pot {position} read incorrectly after split.")
            return sample_label, True

        image_area = pot_img.shape[0] * pot_img.shape[1]
        plot_ix = plot_ix_list[int(position) - 1]
        ## Apply blur ##
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        pot_img = cv2.cvtColor(pot_img, cv2.COLOR_BGR2RGB)
        pot_img = cv2.medianBlur(pot_img, 5)
        # Convert to HSV
        hsv = cv2.cvtColor(pot_img, cv2.COLOR_RGB2HSV)
        # Convert to LAB
        lab = cv2.cvtColor(pot_img, cv2.COLOR_RGB2LAB)

        lower_green = np.array([40, 60, 40])  # lower bound for green in HSV
        upper_green = np.array([95, 255, 200])  # upper bound for green in HSV
        mask_green = cv2.inRange(hsv, lower_green, upper_green)  # mask everything in green range
        mask_lab = cv2.threshold(lab[:, :, 1], 115, 255, cv2.THRESH_BINARY_INV)[1]
        mask_combo = cv2.bitwise_or(mask_lab, mask_green)
        mask_combo = cv2.erode(mask_combo, kernel, iterations=3)
        mask_combo = cv2.dilate(mask_combo, kernel, iterations=3)
        mask_combo = pcv.fill_holes(mask_combo)
        mask_combo = cv2.erode(mask_combo, kernel, iterations=4)
        mask_combo = cv2.dilate(mask_combo, kernel, iterations=4)

        pot_things[position] = {"pot_img": pot_img, "mask_green": mask_green, "mask_lab": mask_lab,
                                "mask_combo": mask_combo}

        plt.subplot(npots, 4, plot_ix)
        plt.imshow(pot_img)
        plt.title(f"Cropped image pot {position}")

        plt.subplot(npots, 4, plot_ix + 1)
        plt.imshow(mask_green)
        plt.title(f"Mask in green range HSV pot {position}")

        plt.subplot(npots, 4, plot_ix + 2)
        plt.imshow(mask_lab)
        plt.title(f"Mask in green range LAB pot {position}")

        plt.subplot(npots, 4, plot_ix + 3)
        plt.imshow(mask_combo)
        plt.title(f"Mask in green range HSV and LAB pot {position}")

    plt.savefig(os.path.join(box_img_out, f"masks_{now}.png"))
    plt.close('all')

    ### BOOST GREEN ###

    for position in range(1, npots + 1):
        pot_img = pot_things[position]["pot_img"]
        mask = pot_things[position]["mask_combo"]
        hsv = cv2.cvtColor(pot_img, cv2.COLOR_RGB2HSV)

        hsv_boosted = hsv.copy()
        hsv_boosted[..., 1] = np.where(mask != 0, np.clip(hsv_boosted[..., 1] * 1.3, 0, 255),
                                       hsv_boosted[..., 1])  # Boost saturation
        hsv_boosted[..., 2] = np.where(mask != 0, np.clip(hsv_boosted[..., 2] * 1.3, 0, 255),
                                       hsv_boosted[..., 2])  # Boost brightness

        hsv_boosted = cv2.bilateralFilter(hsv_boosted, 25, 17, 17)

        rgb_boosted = cv2.cvtColor(hsv_boosted, cv2.COLOR_HSV2RGB)

        pot_things[position]["rgb_boosted"] = rgb_boosted

        # plt.figure(figsize=(12, 12))
        # plt.subplot(2, 2, 1)
        # plt.imshow(pot_img)
        # plt.title(f"Cropped image pot {position}")
        #
        # plt.subplot(2, 2, 2)
        # plt.imshow(rgb_boosted)
        # plt.title(f"Colour adjusted pot {position}")

        # plt.show()

    ### WATERSHED ###

    for position in range(1, npots + 1):

        img = pot_things[position]["rgb_boosted"]
        mask = pot_things[position]["mask_combo"]

        # Noise removal using morphological opening, this reduced segmentation artifacts
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        opening = cv2.dilate(mask, kernel, iterations=3)
        opening = cv2.morphologyEx(opening, cv2.MORPH_OPEN, kernel, iterations=3)

        # Distance transform to highlight object centers, this indicated distance from nearest pixel boundary
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)

        #  Thresholding identifies "sure foreground" regions, what is the areas most likely part of objects.
        _, sure_fg = cv2.threshold(dist_transform, 0.3 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        sure_fg = pcv.fill_holes(sure_fg)

        # Identify the sure background and unknown regions
        sure_bg = cv2.dilate(opening, kernel, iterations=4)
        sure_bg = pcv.fill_holes(sure_bg)

        unknown = cv2.subtract(sure_bg, sure_fg)

        # Create markers for watershed segmentation
        markers = cv2.connectedComponents(sure_fg.astype(np.uint8))[1]
        markers = markers + 1
        markers[unknown == 255] = 0

        watershed_markers = cv2.watershed(img, markers)

        labels = np.unique(watershed_markers)
        rois = []

        for label in labels[2:]:
            target = np.where(watershed_markers == label, 255, 0).astype(np.uint8)
            contours, _ = cv2.findContours(target, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            area = cv2.contourArea(contours[0])
            if area < 0.9 * image_area:
                rois.append(contours[0])

        contour_img = img.copy()
        blank_mask = np.zeros_like(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

        # print(image_area)

        # for i, cnt in enumerate(rois):
        #     temp = blank_mask.copy()
        #     cv2.drawContours(temp, [cnt], -1, 255, cv2.FILLED)
        #     plt.imshow(cv2.cvtColor(temp, cv2.COLOR_BGR2RGB))
        #     plt.title(f"Contour {i} Area {cv2.contourArea(cnt)}")
        #     plt.show()

        contour_img = cv2.drawContours(contour_img, rois, -1, 255, cv2.LINE_AA)
        contour_mask = cv2.drawContours(blank_mask, rois, -1, 255, cv2.FILLED)

        ## Fine tune mask ##
        contour_mask = cv2.erode(contour_mask, kernel, iterations=2)
        contour_mask = cv2.dilate(contour_mask, kernel, iterations=2)
        contour_mask = pcv.fill_holes(contour_mask)
        contour_mask = cv2.erode(contour_mask, kernel, iterations=2)
        contour_mask = cv2.dilate(contour_mask, kernel, iterations=2)

        ## count blobs in image, redraw largest only if there is more than one
        objects, _ = cv2.findContours(contour_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # print(f"Found {len(objects)} object/s")

        if len(objects) > 1:
            max_contour = max(objects, key=len)
            cont = np.vstack([objects[i] for i in range(len(objects))])
            hull = cv2.convexHull(cont)
            cv2.drawContours(opening, [hull], -1, 255, cv2.FILLED)

            # Distance transform to highlight object centers, this indicated distance from nearest pixel boundary
            dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)

            #  Thresholding identifies "sure foreground" regions, what is the areas most likely part of objects.
            _, sure_fg = cv2.threshold(dist_transform, 0.6 * dist_transform.max(), 255, 0)
            sure_fg = np.uint8(sure_fg)
            sure_fg = pcv.fill_holes(sure_fg)

            # Identify the sure background and unknown regions
            sure_bg = cv2.dilate(opening, kernel, iterations=6)

            unknown = cv2.subtract(sure_bg, sure_fg)

            # Create markers for watershed segmentation
            markers = cv2.connectedComponents(sure_fg.astype(np.uint8))[1]
            markers = markers + 1
            markers[unknown == 255] = 0

            watershed_markers = cv2.watershed(img, markers)

            labels = np.unique(watershed_markers)
            rois = []
            for label in labels[2:]:
                target = np.where(watershed_markers == label, 255, 0).astype(np.uint8)
                contours, _ = cv2.findContours(target, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                rois.append(contours[0])

            contour_img = img.copy()
            blank_mask = np.zeros_like(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

            contour_img = cv2.drawContours(contour_img, rois, -1, 255, cv2.LINE_AA)
            contour_mask = cv2.drawContours(blank_mask, rois, -1, 255, cv2.FILLED)

            ## Fine tune mask ##
            contour_mask = cv2.erode(contour_mask, kernel, iterations=3)
            contour_mask = cv2.dilate(contour_mask, kernel, iterations=3)
            contour_mask = pcv.fill_holes(contour_mask)
            contour_mask = cv2.erode(contour_mask, kernel, iterations=3)
            contour_mask = cv2.dilate(contour_mask, kernel, iterations=3)

        pot_things[position]["roi"] = rois
        pot_things[position]["contour_mask"] = contour_mask

        plt.figure(figsize=(9, 6))
        plt.subplot(2, 4, 1)
        plt.imshow(dist_transform)
        plt.title(f"Distance transform {position}")
        plt.subplot(2, 4, 2)
        plt.imshow(sure_fg)
        plt.title(f"Sure foreground {position}")
        plt.subplot(2, 4, 3)
        plt.imshow(sure_bg)
        plt.title(f"Sure background {position}")
        plt.subplot(2, 4, 4)
        plt.imshow(unknown)
        plt.title(f"unknown {position}")

        plt.subplot(2, 4, 5)
        plt.imshow(img)
        plt.title(f"Original image {position}")
        plt.subplot(2, 4, 6)
        plt.imshow(contour_img)
        plt.title(f"Regions of interest {position}")
        plt.subplot(2, 4, 7)
        plt.imshow(contour_mask)
        plt.title(f"Mask to be labelled {position}")

        plt.savefig(os.path.join(box_img_out, f"watershed_{now}_{position}.png"))
        plt.close('all')

    ### LABEL MASK ###

    # Stitch images back together
    mask_tiles = [pot_things[position]["contour_mask"] for position in range(1, npots + 1)]
    mask_rows = [np.hstack(mask_tiles[position * ncols:(position + 1) * ncols]) for position in range(nrows)]
    stitched_mask = np.vstack(mask_rows)
    stitched_mask = pcv.fill_holes(stitched_mask)

    img_tiles = [pot_things[position]["rgb_boosted"] for position in range(1, npots + 1)]
    img_rows = [np.hstack(img_tiles[position * ncols:(position + 1) * ncols]) for position in range(nrows)]
    stitched_img = (cv2.cvtColor(np.vstack(img_rows), cv2.COLOR_BGR2RGB))

    try:
        rois = pcv.roi.auto_grid(mask=stitched_mask, nrows=nrows, ncols=ncols, img=stitched_img,
                                 radius=w // (npots * 2))
        labeled_mask, num_plants = pcv.create_labels(mask=stitched_mask, rois=rois, roi_type="partial")
    except Exception as e:
        log_failure(log_path, sample_label, f"Failed to create mask. [ERROR]: {e} ")
        return sample_label, True

    ### MEASURE SIZE ###

    shape_img = pcv.analyze.size(img=stitched_img, labeled_mask=labeled_mask, n_labels=num_plants)
    shape_img = cv2.cvtColor(shape_img, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(9, 12))
    plt.imshow(labeled_mask)
    plt.title(f"Labeled Mask {rec_date} Box: {boxnum}")
    plt.savefig(os.path.join(box_img_out, f"labelled_mask_{rec_date}_{boxnum}.png"))
    plt.close('all')

    plt.figure(figsize=(9, 12))
    plt.imshow(shape_img)
    plt.title(f"Plant Area {rec_date} Box: {boxnum}")
    plt.savefig(os.path.join(box_img_out, f"area_{rec_date}_{boxnum}.png"))
    plt.close('all')

    ### SAVE OUTPUTS ###

    # Build dataframe
    position = 0
    for label in pcv.outputs.observations:
        position += 1
        observations["date"].append(rec_date)
        observations["box"].append(boxnum)
        observations["position"].append(position)
        observations["height"].append(pcv.outputs.observations[label]['height']['value'] * scale_factor)
        observations["width"].append(pcv.outputs.observations[label]['width']['value'] * scale_factor)
        observations["area"].append(pcv.outputs.observations[label]['area']['value'] * scale_factor ** 2)
        observations["convex_hull_area"].append(
            pcv.outputs.observations[label]['convex_hull_area']['value'] * scale_factor ** 2)
    # print(f"Observations for {sample_label}: \n", observations)

    # Convert entries into dataframe
    df = pd.DataFrame(observations)

    if os.path.exists(size_out_fname):
        # match created dataframe headers to existing csv file headers
        existing_headers = pd.read_csv(size_out_fname, nrows=0, index_col=False).columns.tolist()
        df = df[existing_headers]
        df.to_csv(size_out_fname, mode='a', index=False, header=False)
    else:
        df = df[entries]
        df.to_csv(size_out_fname, mode='w', index=False, header=True)

    # Cleanup
    log_memory("Before cleanup")
    del img, img_cc, img_cc_tray, stitched_img, stitched_mask
    del pot_things, dist_transform, mask_tiles, img_tiles, shape_img
    pcv.outputs.clear()
    plt.close('all')
    gc.collect()
    log_memory("After cleanup")

    return sample_label, False

def iterate_images(img_list, now, outdirs):

    for img in img_list:
        failed = process_image(img, now, outdirs)
    return img, failed

def run_test(img_list):
    import config

    cwd = config.cwd
    now = datetime.datetime.now().strftime("%y%m%d-%H%M")
    photos_dir = config.photos_dir
    outdirs = config.make_outdirs(cwd)

    assert len(img_list) > 0, "No images found in {}".format(photos_dir)
    print("Found {} images".format(len(img_list)))

    iterate_images(img_list, now, outdirs)







