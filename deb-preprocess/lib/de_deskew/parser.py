from decore.parser import Parser

from devision.util.image import ImageHelper

from decore.logging.default_python_logger import DefaultPythonLogger

import os
import numpy as np
from skimage.feature import canny
from skimage.transform import rotate, hough_line, hough_line_peaks
import cv2
from deskew import determine_skew
import math
import pytesseract
import re
import time


class DeSkewParser(Parser):
    piby4 = np.pi / 4

    def __init__(self,
                 r_angle=0,
                 white_bg=False,
                 sigma=3.0,
                 max_peaks=20,
                 flag_smart_peaks_selection=False,
                 logger=None,
                 store_debug_images=False,
                 debug_image_folder="./deskew_debug",
                 debug_saved_basename="deskewed.png"):
        Parser.__init__(self)
        self.r_angle = r_angle
        self.white_bg = white_bg
        self.sigma = sigma
        self.max_peaks = max_peaks
        self.flag_smart_peaks_selection = flag_smart_peaks_selection

        if logger is None:
            logger = DefaultPythonLogger()
        self.logger = logger
        self.store_debug_images = store_debug_images
        self.debug_image_folder = debug_image_folder
        self.debug_saved_basename = debug_saved_basename
        if not os.path.exists(self.debug_image_folder) and self.store_debug_images:
            os.makedirs(self.debug_image_folder)

    @staticmethod
    def calculate_deviation(angle):
        angle_in_degrees = np.abs(angle)
        deviation = np.abs(DeSkewParser.piby4 - angle_in_degrees)
        return deviation

    @staticmethod
    def compare_sum(value):
        if value >= 44 and value <= 46:
            return True
        else:
            return False

    @staticmethod
    def get_max_freq_elem(arr):
        max_arr = []
        freqs = {}
        for i in arr:
            if i in freqs:
                freqs[i] += 1
            else:
                freqs[i] = 1

        sorted_keys = sorted(freqs, key=freqs.get, reverse=True)
        max_freq = freqs[sorted_keys[0]]

        for k in sorted_keys:
            if freqs[k] == max_freq:
                max_arr.append(k)

        return max_arr

    # function to resize the image without distortion i.e resizing with ratios.
    def image_resize(self, image: np.ndarray, width=None, height=None, inter=cv2.INTER_CUBIC):
        # initialize the dimensions of the image to be resized and
        # grab the image size
        dim = None
        (h, w) = image.shape[:2]

        # if both the width and height are None, then return the
        # original image
        if width is None and height is None:
            return image

        # check to see if the width is None
        if width is None:
            # calculate the ratio of the height and construct the
            # dimensions
            r = height / float(h)
            dim = (int(w * r), height)

        # otherwise, the height is None
        else:
            # calculate the ratio of the width and construct the
            # dimensions
            r = width / float(w)
            dim = (width, int(h * r))

        # resize the image
        resized = cv2.resize(image, dim, interpolation=inter)

        # return the resized image
        return resized

    @staticmethod
    def get_otsu(image):
        # binarizing the image using otsu's binarization method
        _, otsu = cv2.threshold(image, 180, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return otsu

    # function to correct the 2d skew of the image

    def get_median_angle(self, binary_image):
        # applying morphological transformations on the binarised image
        # to eliminate maximum noise and obtain text ares only
        erode_otsu = cv2.erode(binary_image, np.ones((7, 7), np.uint8), iterations=1)
        negated_erode = ~erode_otsu
        opening = cv2.morphologyEx(negated_erode, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8), iterations=2)
        double_opening = cv2.morphologyEx(opening, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=5)
        double_opening_dilated_3x3 = cv2.dilate(double_opening, np.ones((3, 3), np.uint8), iterations=4)

        # finding the contours in the morphologically transformed image
        contours_otsu, _ = cv2.findContours(double_opening_dilated_3x3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # iniatialising the empty angles list to collet the angles of each contour
        angles = []

        # obtaining the angles of each contour using a for loop
        for cnt in range(len(contours_otsu)):
            # the last output of the cv2.minAreaRect() is the orientation of the contour
            rect = cv2.minAreaRect(contours_otsu[cnt])

            # appending the angle to the angles-list
            angles.append(rect[-1])

        # finding the median of the collected angles
        angles.sort()
        median_angle = np.median(angles)

        # returning the median angle
        return median_angle

    # funtion to correct the median-angle to give it to the cv2.warpaffine() function
    def corrected_angle(self, angle):
        if 0 <= angle <= 90:
            corrected_angle = angle - 90
        elif -45 <= angle < 0:
            corrected_angle = angle - 90
        elif -90 <= angle < -45:
            corrected_angle = 90 + angle
        return corrected_angle


    def correct_skew(self, image):
        # # resizing the image to 2000x3000 to sync it with
        # #  the morphological tranformations in get_median_angle() function
        # image_resized = self.image_resize(image, 2000, 3000)
        #
        # # getting the binarized image
        # gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
        # otsu = DeSkewParser.get_otsu(gray)
        # # find median of the angles
        # median_angle = self.get_median_angle(otsu)

        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        angle = determine_skew(grayscale)
        if angle is None:
            angle = 0.0

        # # rotating the image
        # skew_angle = self.corrected_angle(angle)

        rotated_image = ImageHelper.rotate(image, angle, (255, 255, 255))
        # after rotating the image using above function, the image is rotated
        # such that the text is alligned along any one of the 4 axes i.e 0, 90, 180 or 270
        # so we are going to use tesseract's image_to_osd function to set it right

        # tesseract's image_to_osd() function works best with images with more visible characters.
        # so we are binarizing the image before passing it to the function
        # otherwise, due to less clarity in the image tesseract raises an expection: 0 dpi exception

        return rotated_image, angle

    def process(self, image):
        corrected_image, skew_angle = self.correct_skew(image)
        return corrected_image, skew_angle

        # res = self.determine_skew(image)
        #
        # try:
        #     angle = res['Estimated Angle']
        #     deskew_angle = res['Average Deviation from pi/4']
        # except Exception:
        #     angle = 0
        #     deskew_angle = 0
        #
        # rot_angle = 0
        # if 0 <= angle <= 90:
        #     rot_angle = angle - 90 + self.r_angle
        # if -45 <= angle < 0:
        #     rot_angle = angle - 90 + self.r_angle
        # if -90 <= angle < -45:
        #     rot_angle = 90 + angle + self.r_angle
        #
        # # dirty fix by gkl, not sure if works
        # if abs(rot_angle) > 80 and rot_angle < 0:
        #     rot_angle = rot_angle + 90
        # if rot_angle > 80:
        #     rot_angle = rot_angle - 90
        #
        # self.logger.info("detected skew", rot_angle)
        #
        # if self.white_bg:
        #     rotated = rotate(image, rot_angle, resize=True, mode="constant", cval=1)
        # else:
        #     rotated = rotate(image, rot_angle, resize=True)
        #
        # rotated = rotated * 255
        # rotated = rotated.astype(np.uint8)
        # print("------------------------------------", rotated, rot_angle)
        # return rotated, deskew_angle, rot_angle

    def determine_skew(self, image):
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        image = ImageHelper.binarize(image)

        edges = canny(image, sigma=self.sigma)

        h, a, d = hough_line(edges)

        # select useful angles based on accums
        if self.flag_smart_peaks_selection:
            self.max_peaks = 100

        try:
            accums, ap, dists = hough_line_peaks(h, a, d, num_peaks=self.max_peaks)
        except Exception:
            return {"Message": "Bad Quality"}
        if len(ap) == 0:
            return {"Message": "Bad Quality"}

        # select useful angles(ap) based on accums statistic
        if self.flag_smart_peaks_selection:
            thred = np.mean(accums) - np.std(accums)
            for i in range(len(accums)):
                if accums[i] < thred:
                    break
            accums = accums[:i]
            ap = ap[:i]
            dists = dists[:i]

        if True:
            # debug info
            # folder_name = os.path.dirname(self.input_file)
            folder_name = self.debug_image_folder
            basename = self.debug_saved_basename
            fname_prefix = basename
            folder_name = os.path.join(folder_name, "skew_debug_" + basename)
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            cv2.imwrite(fname_prefix + "_edges.png", edges * 255)

            image_detectline = image
            row1, col1 = image_detectline.shape
            for _, angle, dist in zip(accums, ap, dists):
                y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
                y1 = (dist - col1 * np.cos(angle)) / np.sin(angle)
                image_detectline = cv2.line(image_detectline, (0, int(y0)), (int(col1), int(y1)), (0, 255, 0))
            cv2.imwrite(fname_prefix + "_detectline.png", image_detectline)

        absolute_deviations = [self.calculate_deviation(k) for k in ap]
        average_deviation = np.mean(np.rad2deg(absolute_deviations))
        ap_deg = [np.rad2deg(x) for x in ap]

        bin_0_45 = []
        bin_45_90 = []
        bin_0_45n = []
        bin_45_90n = []

        for ang in ap_deg:
            print(average_deviation, ang)

            deviation_sum = int(90 - ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_45_90.append(ang)
                continue

            deviation_sum = int(ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_0_45.append(ang)
                continue

            deviation_sum = int(-ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_0_45n.append(ang)
                continue

            deviation_sum = int(90 + ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_45_90n.append(ang)

        angles = [bin_0_45, bin_45_90, bin_0_45n, bin_45_90n]
        lmax = 0

        for j in range(len(angles)):
            l_angles = len(angles[j])
            if l_angles > lmax:
                lmax = l_angles
                maxi = j

        if lmax:
            ans_arr = self.get_max_freq_elem(angles[maxi])
            ans_res = np.mean(ans_arr)

        else:
            ans_arr = self.get_max_freq_elem(ap_deg)
            ans_res = np.mean(ans_arr)

        data = {
            "Average Deviation from pi/4": average_deviation,
            "Estimated Angle": ans_res,
            "Angle bins": angles}
        print("*"*120)
        print(data)

        return data