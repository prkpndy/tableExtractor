import numpy as np
import pandas as pd
import cv2 as cv


def get_contours(image_orig,  # Parameters for PDF were: ev=eh=dv=dh=100, w_ve=w_vd=w_he=w_hd=1, i_ve=i_vd=i_he=i_hd=3
                 w_ve=1, w_vd=3, w_he=1, w_hd=3,
                 i_ve=3, i_vd=5, i_he=3, i_hd=5,
                 ev=100, eh=100, dv=100, dh=100,
                 binarisation_method="otsu"):
    """
    This function takes an image as argument and returns an image with only the vertical and horizontal lines in it.
    Later on this image might be used to get the contours in the original image.

    Input : image_orig --> image to work on
            w_ve --> width of vertical kernel for erosion
            w_vd --> width of vertical kernel for dilation
            w_he --> width of horizontal kernel for erosion
            w_hd --> width of horizontal kernel for dilation
            i_ve --> no. of iterations for vertical erosion
            i_vd --> no. of iterations for vertical dilation
            i_he --> no. of iterations for horizontal erosion
            i_hd --> no. of iterations for horizontal dilation
            ev --> determines the length of vertical kernel for erosion
            eh --> determines the length of horizontal kernel for erosion
            dv --> determines the length of vertical kernel for dilation
            dh --> determines the length of horizontal kernel for dilation

            determination of length is done as follows: length = (size of image in that direction)/value

    Output : img_vh --> image with only vertical and horizontal lines
    """

    if binarisation_method == "otsu":
        blur = cv.GaussianBlur(image_orig, (3, 3), 0)
        _, img_bin = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    elif binarisation_method == "adaptive_thresholding":
        img_bin = cv.adaptiveThreshold(image_orig, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 9, 2)

    # Inverting the colors of a binary image
    img_bin_inv = 255 - img_bin

    # Defining the kernels lengths
    kernel_len_ver_ero = image_orig.shape[0] // ev
    kernel_len_hor_ero = image_orig.shape[1] // eh
    kernel_len_ver_dil = image_orig.shape[0] // dv
    kernel_len_hor_dil = image_orig.shape[1] // dh

    # Defining a vertical kernel to detect all vertical lines of image
    ver_kernel_ero = cv.getStructuringElement(cv.MORPH_RECT, (w_ve, kernel_len_ver_ero))
    ver_kernel_dil = cv.getStructuringElement(cv.MORPH_RECT, (w_vd, kernel_len_ver_dil))
    # Defining a horizontal kernel to detect all horizontal lines of image
    hor_kernel_ero = cv.getStructuringElement(cv.MORPH_RECT, (kernel_len_hor_ero, w_he))
    hor_kernel_dil = cv.getStructuringElement(cv.MORPH_RECT, (kernel_len_hor_dil, w_hd))
    # Defining another kernel
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))

    # Detecting the vertical lines
    image_1 = cv.erode(img_bin_inv, ver_kernel_ero, iterations=i_ve)
    vertical_lines = cv.dilate(image_1, ver_kernel_dil, iterations=i_vd)
    # Detecting the horizontal lines
    image_2 = cv.erode(img_bin_inv, hor_kernel_ero, iterations=i_he)
    horizontal_lines = cv.dilate(image_2, hor_kernel_dil, iterations=i_hd)

    # Combine horizontal and vertical lines in a new third image, with both having same weight.
    img_vh = cv.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)

    # Eroding and thresholding (binarising) the image
    img_vh = cv.erode(~img_vh, kernel, iterations=2)
    _, img_vh = cv.threshold(img_vh, 128, 255, cv.THRESH_BINARY)

    return img_vh


def get_bounds(contours, shape, x, y):
    """
    This function returns the position of the row and the column lines.
    Input: contours --> contours detected in the table
           shape --> shape of the image (to estimate the buffer)
           x --> used to calculate the buffer for columns
           y --> used to calculate the buffer for rows

    Output: rows --> points along the Y-axis where a row line should be drawn
            cols --> points along the X-axis where a column line should be drawn
    """

    # Estimating the buffer from the shape of the image
    ty = shape[0] // y
    tx = shape[1] // x
    rows = []
    cols = []
    rows_temp = []
    cols_temp = []

    # Loop to get the rows and the column bounds
    for contour in contours:
        flag = 0
        for row, r in zip(rows, rows_temp):
            if ((np.mean(row) - ty) < contour[1]) and ((np.mean(row) + ty) > contour[1]):
                row.append(contour[1])
                r.append(contour[1] + contour[3])
                flag = 1
                break
        if not flag:
            rows.append([contour[1]])
            rows_temp.append([contour[1] + contour[3]])

        flag = 0
        for col, c in zip(cols, cols_temp):
            if ((np.mean(col) - tx) < contour[0]) and ((np.mean(col) + tx) > contour[0]):
                col.append(contour[0])
                c.append(contour[2] + contour[0])
                flag = 1
                break
        if not flag:
            cols.append([contour[0]])
            cols_temp.append([contour[2] + contour[0]])

    rows = [np.mean(v) for v in rows]
    cols = [np.mean(v) for v in cols]
    rows_temp = [np.mean(v) for v in rows_temp]
    cols_temp = [np.mean(v) for v in cols_temp]
    rows.sort()
    cols.sort()
    rows_temp.sort()
    cols_temp.sort()
    rows.append(rows_temp[-1])
    cols.append(cols_temp[-1])
    return rows, cols


def inside(outer, inner):
    """
    This function determines whether the inner box is inside the outer box.

    Input: outer --> the outer box (should be of the form [x, y, width, height])
           inner --> the inner box (should be of the form [x1, y1, x2, y2] in the anti-clockwise direction starting from
                     the upper left corner)
    Output: True --> if the inner box is inside the outer box
            False --> if the inner box is not inside the outer box
    """
    if (outer[0] > inner[0]) or (outer[1] > inner[1]):
        return False
    if (inner[2] > (outer[0] + outer[2])) or (inner[3] > (outer[1] + outer[3])):
        return False
    return True


def data_to_dataframe(list_row_col, col_count, table_no, table_bounds):
    """
    This function takes the data in the form of list of dictionary and returns a dictionary.

    Input: list_row_cols --> list of dictionary containing data in the form [ {row: , col: , content: }, ... ]
           col_count --> number of columns in the data-frame
           table_no --> the table number
           table_bounds --> the table bounds in the form [x, y, width, height]
    Output: dictionary of the form {bbox: , table_no: , content: }
    """

    data = {'col' + str(i): [] for i in range(col_count)}

    for d in list_row_col:
        data['col' + str(d['col'])].append(d['content'])

    data = {k: pd.Series(v) for k, v in data.items()}

    df = pd.DataFrame(data)

    return {'bbox': table_bounds, 'table_no': table_no, 'content': df}


def get_orientation(page_info, table):
    # TODO: add functionality for pi radians of rotation
    """
    This function tells the orientation of the image (n*pi/2 radians rotation in clockwise direction considering
    Portrait as 0 radians) based on the output of google_ocr

    Input : page_info --> the output of read_image_gocr.parse_image() for a particular image
            table --> the coordinates of the table in the format [x, y, w, h]

    Output : 0 --> 0 radians rotation (Portrait)
             1 --> pi/2 radians rotation (Landscape)
             2 --> pi radians rotation (Portrait)
             3 --> 3pi/2 radians rotation (Landscape)
    """
    w_bbox = [(b['x2'] - b['x1'], b['y2'] - b['y1']) for b in page_info if inside(table, list(b.values())[:4])]
    if not w_bbox:
        return None
    w_bbox = np.array(w_bbox)
    mean = np.mean(w_bbox, 0)
    ratio = mean[1]/mean[0]
    if (ratio > 0) and (ratio < 1) and (mean[1] > 0) and (mean[0] > 0):
        return 0
    elif (ratio < -1) and (mean[0] < 0) and (mean[1] > 0):
        return 1
    elif (ratio > 0) and (ratio < 1) and (mean[0] < 0) and (mean[1] < 0):
        return 2
    elif (ratio < -1) and (mean[0] > 0) and (mean[1] < 0):
        return 3
    else:
        return None


if __name__ == '__main__':
    import pickle
    pkfile = open('page_info270.pk', 'rb')
    page_info = pickle.load(pkfile)
    pkfile.close()
    print(page_info)
    print(get_orientation(page_info, (0, 0, 2000, 3000)))


def binarise(image, sx, sy, c):
    x = 0
    y = 0
    print(image.shape)
    for c1 in range(image.shape[0]//sy):
        x = 0
        for c2 in range(image.shape[1]//sx):
            m = np.mean(image[y:(y+sy), x:(x+sx)])
            for iy in range(y, y+sy):
                for ix in range(x, x+sx):
                    if image[iy, ix] <= (m-c):
                        image[iy, ix] = 0
                    else:
                        image[iy, ix] = 255
            x = x + sx
        m = np.mean(image[y:(y+sy), x:])
        for iy in range(y, y + sy):
            for ix in range(x, image.shape[1]):
                if image[iy, ix] <= (m - c):
                    image[iy, ix] = 0
                else:
                    image[iy, ix] = 255
        y = y + sy

    x = 0
    if y < image.shape[0]:
        for c2 in range(image.shape[1]//sx):
            m = np.mean(image[y:, x:(x+sx)])
            for iy in range(y, image.shape[0]):
                for ix in range(x, x+sx):
                    if image[iy, ix] <= (m - c):
                        image[iy, ix] = 0
                    else:
                        image[iy, ix] = 255
            x = x + sx
        for iy in range(y, image.shape[0]):
            for ix in range(x, image.shape[1]):
                if image[iy, ix] <= (m - c):
                    image[iy, ix] = 0
                else:
                    image[iy, ix] = 255

    # cv.imwrite('test.jpg', image)
    return image
