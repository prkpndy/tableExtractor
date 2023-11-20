import cv2 as cv
import numpy as np
from scipy.ndimage import interpolation as inter


def correct_skew(image_name, image_path, delta=0.5, limit=10):
    """
    This function takes the image name and path and corrects the skew in it
    Input: image_name --> name of the image
           image_path --> path of the image
           delta
           limit
    It saves the skew corrected image in the image_path location with the same name
    """
    def determine_score(arr, angle):
        data = inter.rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2)
        return histogram, score

    image = cv.imread(image_path + image_name)
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]

    scores = []
    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        histogram, score = determine_score(thresh, angle)
        scores.append(score)

    best_angle = angles[scores.index(max(scores))]

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv.getRotationMatrix2D(center, best_angle, 1.0)
    rotated = cv.warpAffine(image, M, (w, h), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)
    cv.imwrite(image_path + image_name, rotated)
    print("skew angle -->", best_angle)
    # return best_angle, rotated


if __name__ == '__main__':
    image = cv.imread('data_pdf4/photo/photo-1.jpg')
    angle, rotated = correct_skew(image)
    print(angle)
    cv.imwrite('rotated.jpg', rotated)