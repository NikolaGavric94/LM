import cv2 as cv
import numpy as np
import pyautogui


class Vision:
    reader = None
    window_offset = None

    def __init__(self, reader, window_offset):
        self.window_offset = window_offset
        self.reader = reader
        print ('Vision initialized.')

    def find(self, haystack_img, needle_img, threshold = .9):
        # check the current screenshot for the limestone tooltip using match template
        result = cv.matchTemplate(haystack_img, needle_img, cv.TM_CCOEFF_NORMED)
        # get the best match postition
        _, max_val, _, (x, y) = cv.minMaxLoc(result)
        # Print best match
        # print ('Best match %f and threshold is %f' % (max_val, threshold))
        # if we can closely match the tooltip image, consider the object found
        if max_val >= threshold:
            return True, self.get_screen_position([x,y])
        
        try:
            found = pyautogui.locateOnScreen(needle_img, confidence=threshold, grayscale=True)
            (x, y, _, _) = found
            return True, (x, y)
        except:
            pass
        
        return False, None
    
    # translate a pixel position on a screenshot image to a pixel position on the screen.
    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    def read(self, needle_img, threshold=0.9):
        """Extract text from an image using EasyOCR and return the result with the highest accuracy."""
        # Extract results that meet the threshold
        results = self.reader.readtext(needle_img, text_threshold=threshold, low_text=0.4)
        return results

    # given a list of [x, y, w, h] rectangles returned by find(), convert those into a list of
    # [x, y] positions in the center of those rectangles where we can click on those found items
    def get_click_point(self, rectangle):
        (x, y, w, h) = rectangle
        center_x = x + int(w/2)
        center_y = y + int(h/2)

        return (center_x, center_y)

    # given a list of [x, y, w, h] rectangles and a canvas image to draw on, return an image with
    # all of those rectangles drawn
    def draw_rectangles(self, haystack_img, rectangles):
        # these colors are actually BGR
        line_color = (0, 255, 0)
        line_type = cv.LINE_4

        for (x, y, w, h) in rectangles:
            # determine the box positions
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            # draw the box
            cv.rectangle(haystack_img, top_left, bottom_right, line_color, lineType=line_type)

        return haystack_img

    # given a list of [x, y] positions and a canvas image to draw on, return an image with all
    # of those click points drawn on as crosshairs
    def draw_crosshairs(self, haystack_img, point):
        # these colors are actually BGR
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS
        (center_x, center_y) = point
        cv.drawMarker(haystack_img, (center_x, center_y), marker_color, marker_type)

        return haystack_img