import cv2 as cv
import keyboard
from time import time, sleep
from threading import Thread, Lock
import os
from pretty_time import pretty_date
import pyautogui

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their 
# own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class BotState:
    INITIALIZING = 0
    IDLE = 1
    GATHERING_LOCATIONS = 2
    CHECKING_BALANCE = 3
    APPLYING_SHIELD = 4
    COLLECTING_HELP = 5
    COLLECTING_MYSTERY_BOX = 6
    CHECKING_SHIELD = 7

class LMBot:
    # housekeeper #1
    housekeeper = None

    # constants
    SHIELD_TIMER = 0
    RESOURCES_MATCH_THRESHOLD = 0.975
    INITIALIZING_SECONDS = 7

    # threading properties
    stopped = True
    lock = None

    # properties
    reader = None
    state = None
    targets = []
    screenshot = None
    timestamp = None
    window_offset = (0,0)
    window_w = 0
    window_h = 0
    middle_x = 0
    middle_y = 0

    def __init__(self, window_offset, window_size, housekeeper):
        # start bot in the initializing mode to allow us time to get setup.
        # mark the time at which this started so we know when to complete it
        self.state = BotState.INITIALIZING
        self.timestamp = time()

        # create a thread lock object
        self.lock = Lock()

        # for translating window positions into screen positions, it's easier to just
        # get the offsets and window size from WindowCapture rather than passing in 
        # the whole object
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]
        self.middle_x = self.window_offset[0] + (self.window_w // 2)
        self.middle_y = self.window_offset[1] + (self.window_h // 2)
        self.housekeeper = housekeeper
        print ('LM Bot initialized.')

    def use_shield(self):
        pyautogui.click(self.housekeeper.shield_loc[0], self.housekeeper.shield_loc[1])
        pyautogui.click(self.housekeeper.use_shield_loc[0], self.housekeeper.use_shield_loc[1])
        self.close(2)

    def open_shield_boost(self):
        pyautogui.click(self.housekeeper.turf_boost_loc[0], self.housekeeper.turf_boost_loc[1])
        pyautogui.vscroll(1000, self.middle_x, self.middle_y)

    def close(self, counter=1, interval=0):
        pyautogui.press('esc', presses=counter, interval=interval)

    def open_shield_records(self):
        pyautogui.click(self.housekeeper.turf_boost_loc[0], self.housekeeper.turf_boost_loc[1])
        pyautogui.vscroll(1000, self.middle_x, self.middle_y)
        pyautogui.click(self.housekeeper.shield_records_loc[0], self.housekeeper.shield_records_loc[1])

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the WindowCapture __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    # main logic controller
    def run(self):
        while not self.stopped:
            if self.state == BotState.INITIALIZING:
                # do no bot actions until the startup waiting period is complete
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    # start searching when the waiting period is over
                    self.lock.acquire()
                    self.state = BotState.GATHERING_LOCATIONS
                    self.lock.release()
            elif self.state == BotState.IDLE:
                # save pc resources by not straining CPU that often
                # otherwise remove the below --- if --- statement
                if not self.housekeeper.is_shield_active():
                    print ('Listening for hostilities...')
                    notifications = self.housekeeper.listen_for_notifications(self.screenshot)
                    if any(notifications):
                        self.lock.acquire()
                        self.state = BotState.CHECKING_SHIELD
                        self.lock.release()