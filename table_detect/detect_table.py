import cv2 as cv
import numpy as np
from multi_level_table import functions


def sort_contours_toptobottom(contours):
    # initialize the reverse flag and sort index
    reverse = False
    i = 1
    bounding_boxes = [cv.boundingRect(c) for c in contours]
    (contours, bounding_boxes) = zip(*sorted(zip(contours, bounding_boxes), key=lambda b: b[1][i], reverse=reverse))
    # return the list of sorted contours and bounding boxes
    return contours, bounding_boxes


def detect_table(image_file):
    """
    This function takes image_file as an input and returns a list of lists where each list contains the bounds of a
    table in the form [x, y, width, height]

    Input: image_file --> the path of the image from which the table location is to be extracted
    Output: a list of lists containing the location of each table in the image
    """

    image = cv.imread(image_file)
    image_orig = cv.imread(image_file, 0)
    shape = image_orig.shape

    # Parameters earlier --> 1, 2, 1, 3, 3, 3, 3, 3, 150, 120, 50, 50
    img_vh = functions.get_contours(image_orig,
                                    w_vd=2, i_ve=3, i_vd=3, i_he=3, i_hd=3, ev=150, eh=120, dv=50, dh=50,
                                    binarisation_method="adaptive_thresholding")

    # Finding the contours in the image
    contours, hierarchy = cv.findContours(img_vh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    cells = []

    for c, h in zip(contours, hierarchy[0]):
        if h[2] == -1:
            cells.append(c)

    img = np.zeros(shape, dtype=np.uint8)
    img.fill(255)

    for cell in cells:
        x, y, w, h = cv.boundingRect(cell)
        if (w < 9*shape[1]/10) and (h < 9*shape[0]/10):
            img = cv.rectangle(img, (x-15, y-15), (x + w + 15, y + h + 15), (0, 255, 0), -1)

    img = 255 - img
    cntrs, _ = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    tables = []

    for cntr in cntrs:
        x, y, w, h = cv.boundingRect(cntr)
        if (h > shape[0]/15) and (w > shape[1]/8):
            if (h != shape[0]) or (w != shape[1]):
                tables.append(cntr)

    if len(tables) != 0:
        _, tables = sort_contours_toptobottom(tables)
        for t in tables:
            image = cv.line(image, (t[0], t[1]+t[3]-5), (t[0]+t[2], t[1]+t[3]-5), (0, 0, 0), 2)
            image = cv.line(image, (t[0], t[1]+5), (t[0]+t[2], t[1]+5), (0, 0, 0), 2)
        cv.imwrite(image_file, image)

    return tables
