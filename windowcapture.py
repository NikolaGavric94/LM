import numpy as np
import win32gui
import mss
from threading import Thread, Lock
from PIL import Image

class WindowCapture:

    # threading properties
    stopped = True
    lock = None
    screenshot = None
    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # constructor
    def __init__(self, window_name=None):
        # create a thread lock object
        self.lock = Lock()

        # find the handle for the window we want to capture.
        # if no window name is given, capture the entire screen
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # account for the window border and titlebar and cut them off
        border_pixels = 1
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y
        print ('Window capture initialized.')

    def get_screenshot(self):
        try:
            with mss.mss() as sct:
                screenshot = sct.grab({
                    'top': self.offset_y,
                    'left': self.offset_x,
                    'width': self.w,
                    'height': self.h
                })

                # Convert the screenshot to a NumPy array (BGRA format)
                img = np.array(screenshot)
                
                # Drop the alpha channel (BGRA -> BGR)
                img = img[..., :3]

                # Make the image C_CONTIGUOUS for better performance
                img = np.ascontiguousarray(img)

            return img

        except Exception as e:
            raise RuntimeError(f"Failed to capture screenshot: {e}")

    # threading methods
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        # continuously capture the screenshot and update the image
        while not self.stopped:
            screenshot = self.get_screenshot()
            # Lock the thread while updating the results
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()