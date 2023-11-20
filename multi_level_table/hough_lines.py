import cv2 as cv
import numpy as np


def hough_lines(image):
    shape = image.shape
    dst = cv.Canny(image, 50, 200, None, 3)

    img = np.zeros(shape, dtype=np.uint8)
    img.fill(255)

    lines = cv.HoughLines(dst, 1, np.pi / 90, 120, None, 0, 0)
    t = 20
    if lines is not None:
        rv = []
        rh = []
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            if (theta < 0.1) and (theta > -0.1):
                flag = False
                for r in rv:
                    if (rho > (np.mean(r) - t)) and (rho < (np.mean(r) + t)):
                        r.append(rho)
                        flag = True
                        break
                if not flag:
                    rv.append([rho])
            elif (theta > 1.5) and (theta < 1.6):
                flag = False
                for r in rh:
                    if (rho > (np.mean(r) - t)) and (rho < (np.mean(r) + t)):
                        r.append(rho)
                        flag = True
                        break
                if not flag :
                    rh.append([rho])

        for r in rh:
            r = int(np.mean(r))
            cv.line(img, (0, r), (shape[1], r), color=0, thickness=1)
        for r in rv:
            r = int(np.mean(r))
            cv.line(img, (r, 0), (r, shape[0]), color=0, thickness=1)
    return img
        # cv.imwrite('../output_image3.jpg', image_c)


if __name__ == '__main__':
    hough_lines(cv.imread('../data/test_pictures/table_photo-3.jpg', 0))