import cv2 as cv


def detect_table(image_orig):
    # image_orig = cv.imread(image_file, 0)
    shape = image_orig.shape
    # converting the image to a binary image
    # print(shape)
    # img_bin = cv.adaptiveThreshold(image_orig, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 9, 2)
    _, img_bin = cv.threshold(image_orig, 140, 255, cv.THRESH_BINARY)

    # inverting the image
    img_bin_inv = 255 - img_bin

    kernel_len_ver_ero = image_orig.shape[0] // 100
    kernel_len_hor_ero = image_orig.shape[1] // 100
    kernel_len_ver_dil = image_orig.shape[0] // 100
    kernel_len_hor_dil = image_orig.shape[1] // 100
    # Defining a vertical kernel to detect all vertical lines of image
    ver_kernel_ero = cv.getStructuringElement(cv.MORPH_RECT, (1, kernel_len_ver_ero))
    ver_kernel_dil = cv.getStructuringElement(cv.MORPH_RECT, (1, kernel_len_ver_dil))
    # Defining a horizontal kernel to detect all horizontal lines of image
    hor_kernel_ero = cv.getStructuringElement(cv.MORPH_RECT, (kernel_len_hor_ero, 1))
    hor_kernel_dil = cv.getStructuringElement(cv.MORPH_RECT, (kernel_len_hor_dil, 1))
    # A kernel of 2x2
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))

    image_1 = cv.erode(img_bin_inv, ver_kernel_ero, iterations=3)
    vertical_lines = cv.dilate(image_1, ver_kernel_dil, iterations=3)

    image_2 = cv.erode(img_bin_inv, hor_kernel_ero, iterations=3)
    horizontal_lines = cv.dilate(image_2, hor_kernel_dil, iterations=3)

    img_vh = cv.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
    # cv.imwrite('tab.jpg', img_vh)
    img_vh = cv.erode(~img_vh, kernel, iterations=2)
    _, img_vh = cv.threshold(img_vh, 128, 255, cv.THRESH_BINARY)

    # cv.imwrite('table.jpg', img_vh)

    img_vh = 255-img_vh

    breakpoints = []
    count = 0
    while True:
        if sum(img_vh[count, :]) == 0:
            if count == img_vh.shape[0]:
                breakpoints.append((count, count))
            else:
                start = count
                flag = False
                for r in img_vh[(count+1):, :]:
                    if sum(r) == 0:
                        count += 1
                    else:
                        end = count
                        flag = True
                        break
                if not flag:
                    end = count
                breakpoints.append((start, end))
                count = end + 1
        count += 1
        if count >= img_vh.shape[0]:
            break

    r_bp = []

    for bp in breakpoints:
        if (bp[0] > 10) and (bp[1] < (shape[0] - 10)):
            r_bp.append(bp)

    breakpoints = r_bp
    tables = []

    if len(breakpoints) != 0:
        ep = 0
        for bp in breakpoints:
            h = bp[0] - ep
            tables.append((0, ep, shape[1], h))
            ep = bp[1]
        tables.append((0, ep, shape[1], shape[0] - ep))
    # else:
    #     tables.append([0, 0, shape[1], shape[0]])

    r_tb = []
    th_y = shape[0]//200
    th_x = shape[1]//200
    for bp in tables:
        if (bp[2] > th_x) and (bp[3] > th_y):
            r_tb.append(bp)

    tables = r_tb

    # im_o = cv.imread(image_file)
    # for t in tables:
    #     im_o = cv.rectangle(im_o, (t[0], t[1]), (t[0]+t[2], t[1]+t[3]), (255, 0, 0), 3)
    # cv.imwrite('ans2.jpg', im_o)
    return tables


if __name__ == '__main__':
    print(detect_table('photo/photo-07.jpg'))
