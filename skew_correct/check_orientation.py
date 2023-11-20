import pytesseract
import cv2 as cv
import os
import numpy as np


def get_orientation(image_name, image_path):
    image = cv.imread(os.path.join(image_path, image_name))
    print(pytesseract.image_to_osd(image))
    data = pytesseract.image_to_data(image, 'eng')
    sent = data.split('\n')
    l = []
    for s in sent:
        l += s.split('\t')
    x = [int(i) for i in l[18::12]]
    y = [int(i) for i in l[19::12]]
    w = [int(i) for i in l[20::12]]
    h = [int(i) for i in l[21::12]]
    bbox = list(zip(x, y, w, h))
    conf = [int(i) for i in l[22::12]]
    bbox = [bbox[i] for i in range(len(bbox)) if conf[i] != -1]
    for b in bbox:
        cv.rectangle(image, (b[0], b[1]), (b[0]+b[2], b[1]+b[3]), (0, 255, 0), -1)
    cv.imwrite('photo2.jpg', image)
    wh = [b[2:] for b in bbox]
    wh = np.array(wh)
    wh = np.mean(wh, 0)
    conf_90 = wh[1]/wh[0]
    print(conf_90)
    text = l[23::12]
    print(text)


if __name__ == '__main__':
    image_path = ''
    # image_name = 'pdf2photo-1.jpg'
    image_name = 'new_pdfphoto-32.jpg'
    get_orientation(image_name, image_path)