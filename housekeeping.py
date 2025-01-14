import cv2
import numpy as np
import pyautogui
from time import sleep
from math import dist
from random import randrange
import os
from time import time
from pretty_time import compare_dates

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their 
# own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Notification:
    ATTACK = 'Attack'
    SCOUT = 'Scout'
    REINFORCEMENT = 'Reinforcement'
    SUPPLY = 'Supply'

class Housekeeper:
    # Vision of the UI
    vision = None
    # Check balance command known image locations
    open_resources_loc = None
    resources_loc = None
    close_resources_loc = None
    ## Various balance related data
    last_balance = None
    last_balance_need_refresh = True
    # Shield and check shield duration image locations
    turf_boost_imgs = ['images/items/turf_boosts.png', 'images/items/turf_boosts_2.png']
    turf_boost_loc = None
    shield_loc = None
    use_shield_loc = None
    shield_records_loc = None
    shielded_at = None
    shield_status_roi = None
    # Notification locations
    attack_notif_loc = None
    scout_notif_loc = None
    reinforcement_notif_loc = None
    supply_notif_loc = None
    last_notif_timestamp = None
    last_notif = None

    def __init__(self, vision):
        self.vision = vision
        print ('Housekeeper initialized.')
    
    def open_resources(self, screenshot):
        if self.open_resources_loc is None:
            food_img = cv2.imread('images/resources/food.png', cv2.IMREAD_GRAYSCALE)
            # make sure depth is 3 to be able to convert to color
            if len(screenshot.shape) == 3:
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            found, (x, y) = self.vision.find(screenshot, food_img, .8)
            
            if not found:
                sleep(1)
                return self.open_resources(screenshot)
            
            # get height and width of image to get full position
            h, w = food_img.shape
            x, y = self.vision.get_click_point((int(x), int(y), int(w), int(h)))
            self.open_resources_loc = (int(x), int(y), int(w), int(h))
            print ("Location of the food resource icon saved at: [%i, %i, %i, %i]" % (self.open_resources_loc))
            pyautogui.click(x, y)
        return True
    
    def locate_resources_balance(self, screenshot):
        if self.resources_loc is None:
            resource_img = cv2.imread('images/sections/resource.png', cv2.IMREAD_GRAYSCALE)
            # make sure depth is 3 to be able to convert to color
            if len(screenshot.shape) == 3:
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            found, (x, y) = self.vision.find(screenshot, resource_img, .9)
            
            if not found:
                sleep(1)
                return self.read_resources_balance(screenshot)
            
            # get height and width of image to get full position
            h, w = resource_img.shape
            self.resources_loc = (int(x), int(y+h), int(w), int(h*5))
            print ("Location of resources text saved at: [%i, %i, %i, %i]" % (self.resources_loc))

        return True
        
    def read_resources_balance(self, balance_screenshot):
        # get resource loc relative to the screen
        x, y, w, h = self.resources_loc
        # get region for pyautogui, need to add offsets because it's not relative to window but screen
        balance_roi = (x, y, w, h)
        balance_screenshot = pyautogui.screenshot(region=balance_roi)
        balance_screenshot = cv2.cvtColor(np.array(balance_screenshot), cv2.COLOR_RGBA2GRAY)
        results = self.vision.read(balance_screenshot, .9)
        return " ".join([result[1] for result in results]).split()
    
    def open_and_save_resources(self, screenshot):
        if not self.last_balance_need_refresh:
            return self.last_balance
        # last balance needs refresh, go ahead and do it
        opened_resources = self.open_resources(screenshot)
        # wait for resources to open
        sleep(1)
        found_balance = self.locate_resources_balance(screenshot)
        read_balance = self.read_resources_balance(screenshot)

        # check if all things went well
        if all([opened_resources, found_balance, read_balance]):
            res_names = ['Food', 'Stone', 'Wood', 'Ore', 'Gold']
            self.last_balance = ' '.join(f"{text} {res_names[i]}" for i, text in enumerate(read_balance))
            return True
        return False

    def open_turf_boosts(self, screenshot, i=0):
        if self.turf_boost_loc is None:
            turf_boost_img = cv2.imread(self.turf_boost_imgs[i], cv2.IMREAD_GRAYSCALE)
            # make sure depth is 3 to be able to convert to color
            if len(screenshot.shape) == 3:
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            found, pos = self.vision.find(screenshot, turf_boost_img, .9)
            
            if not found:
                sleep(1)
                return self.open_turf_boosts(screenshot, i+1)
            
            # get height and width of image to get full position
            x, y = pos
            h, w = turf_boost_img.shape
            x, y = self.vision.get_click_point((int(x), int(y), int(w), int(h)))
            self.turf_boost_loc = (int(x), int(y), int(w), int(h))
            print ("Location of turf boost saved at: [%i, %i, %i, %i]" % (self.turf_boost_loc))
            pyautogui.click(x, y)

        return True

    def open_shield_boost(self, screenshot):
        sleep(1)
        if self.shield_loc is None:
            shield_icon_img = cv2.imread('images/items/shield_icon.png', cv2.IMREAD_GRAYSCALE)
            # make sure depth is 3 to be able to convert to color
            if len(screenshot.shape) == 3:
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            found, (x, y) = self.vision.find(screenshot, shield_icon_img, .9)
            
            if not found:
                sleep(1)
                return self.open_shield_boost(screenshot)
            
            # get height and width of image to get full position
            h, w = shield_icon_img.shape
            x, y = self.vision.get_click_point((int(x), int(y), int(w), int(h)))
            self.shield_loc = (int(x), int(y), int(w), int(h))
            print ("Location of shield saved at: [%i, %i, %i, %i]" % (self.shield_loc))
            pyautogui.click(x, y)

        return True
    
    def save_use_shield_loc(self, screenshot):
        sleep(1)
        if self.use_shield_loc is None:
            use_shield_img = cv2.imread('images/buttons/use.png', cv2.IMREAD_GRAYSCALE)
            # make sure depth is 3 to be able to convert to color
            if len(screenshot.shape) == 3:
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            found, (x, y) = self.vision.find(screenshot, use_shield_img, .9)
            
            if not found:
                sleep(1)
                return self.open_shield_boost(screenshot)
            
            # get height and width of image to get full position
            h, w = use_shield_img.shape
            x, y = self.vision.get_click_point((int(x), int(y), int(w), int(h)))
            self.use_shield_loc = (int(x), int(y), int(w), int(h))
            print ("Location of use shield saved at: [%i, %i, %i, %i]" % (self.use_shield_loc))

        return True
    
    def listen_for_attacks(self, screenshot):
        attack_notif_img = cv2.imread('images/notifications/enemy_attack.png', cv2.IMREAD_GRAYSCALE)
        # make sure depth is 3 to be able to convert to color
        if len(screenshot.shape) == 3:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        found, loc = self.vision.find(screenshot, attack_notif_img, .9)

        if not found:
            return False
        
        if self.attack_notif_loc is None:
            x, y = loc
            h, w = attack_notif_img.shape
            self.attack_notif_loc = (int(x), int(y), int(w), int(h))
        # store last notification time and type
        self.last_notif_timestamp = time()
        self.last_notif = Notification.ATTACK
        print ("Location of attack notification saved at: [%i, %i, %i, %i]" % (self.attack_notif_loc))

        return True
    
    def listen_for_scouts(self, screenshot):
        scout_notif_img = cv2.imread('images/notifications/enemy_scout.png', cv2.IMREAD_GRAYSCALE)
        # make sure depth is 3 to be able to convert to color
        if len(screenshot.shape) == 3:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        found, loc = self.vision.find(screenshot, scout_notif_img, .9)

        if not found:
            return False
        
        if self.scout_notif_loc is None:
            x, y = loc
            h, w = scout_notif_img.shape
            self.scout_notif_loc = (int(x), int(y), int(w), int(h))
        # store last notification time and type
        self.last_notif_timestamp = time()
        self.last_notif = Notification.SCOUT
        print ("Location of attack notification saved at: [%i, %i, %i, %i]" % (self.scout_notif_loc))

        return True
    
    def listen_for_notifications(self, screenshot):
        # self.listen_for_reinforcements(screenshot)
        # self.listen_for_supply(screenshot)
        return [self.listen_for_attacks(screenshot), self.listen_for_scouts(screenshot)]
    
    def is_shielded(self, screenshot):
        # cant find this image because of how filled the bar can be
        # easy solution is to check if the image without the shield exists on screen, if not we are shielded
        # hard solution will be to somehow read the timer efficiently and have the timer always
        # another quicker way to read if we are shielded is to check if the icon in turf is second one in array of turf_boosts_imgs
        # with the above approach we cant rely on shield timer tho so needs to be removed
        shield_img = cv2.imread('images/items/turf_boosts_2.png', cv2.IMREAD_GRAYSCALE)
        # make sure depth is 3 to be able to convert to color
        if len(screenshot.shape) == 3:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        found, _ = self.vision.find(screenshot, shield_img, .9)
        
        if not found:
            self.shielded_at = None
            return False

        return True
    
    def open_and_save_records_loc(self, screenshot):
        if self.shield_records_loc is None:
            records_img = cv2.imread('images/sections/records.png', cv2.IMREAD_GRAYSCALE)
            # make sure depth is 3 to be able to convert to color
            if len(screenshot.shape) == 3:
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            found, loc = self.vision.find(screenshot, records_img, .9)

            if not found:
                sleep(1)
                return self.open_and_save_records_loc(screenshot)
            
            # get height and width of image to get full position
            x, y = loc
            h, w = records_img.shape
            x, y = self.vision.get_click_point((int(x), int(y), int(w), int(h)))
            self.shield_records_loc = (int(x), int(y), int(w), int(h))
            print ("Location of shield records saved at: [%i, %i, %i, %i]" % (self.shield_records_loc))
            pyautogui.click(x, y)

        return True
    
    def find_shield_status_loc(self, screenshot):
        if self.shield_status_roi is None:
            records_img = cv2.imread('images/sections/shield_records.png', cv2.IMREAD_GRAYSCALE)
            # make sure depth is 3 to be able to convert to color
            if len(screenshot.shape) == 3:
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            found, loc = self.vision.find(screenshot, records_img, .9)

            if not found:
                sleep(1)
                return self.find_shield_status_loc(screenshot)
            
            # get height and width of image to get full position
            x, y = loc
            h, w = records_img.shape
            self.shield_status_roi = (int(x), int(y+h), int(w), int(h))
            print ("Location of shield records saved at: [%i, %i, %i, %i]" % (self.shield_status_roi))

        return True
    
    def read_shield_status_loc(self, records_screenshot):
        # get latest shield status loc relative to the screen
        x, y, w, h = self.shield_status_roi
        # get region for pyautogui
        shield_status_roi = (x, y, w, h)
        records_screenshot = pyautogui.screenshot(region=shield_status_roi)
        records_screenshot = cv2.cvtColor(np.array(records_screenshot), cv2.COLOR_RGBA2GRAY)
        results = self.vision.read(records_screenshot, .9)
        return " ".join([result[1] for result in results]).split()
    
    def save_shield_time(self, time):
        # ['01/14/25', '18.15.40', 'Estimated', '01/14/25', '22.15.40'] example time
        # if any(t == 'Estimated' for t in time) and len(time) == 5:
        # ^ this means we are shielded ^
        if len(time) < 4 or len(time) > 5:
            print ('Houston we have a problem with shield status identifying')
            return False
        dt = time[-2:]
        compare_dates(" ".join(dt))

    
    def scroll_top_of_boosts(self):
        pyautogui.vscroll(1000, self.turf_boost_loc[0]/2, self.turf_boost_loc[1])
    
    def close(self, counter=1):
        pyautogui.press('esc', presses=counter)

    def initialize(self, screenshot):
        print ('Initializing housekeeping')
        # save open resources loc
        # self.open_and_save_resources(screenshot)
        # self.close()
        # open and save location of stuff for shielding
        self.open_turf_boosts(screenshot)
        self.scroll_top_of_boosts()
        self.open_and_save_records_loc(screenshot)
        self.find_shield_status_loc(screenshot)
        read = self.read_shield_status_loc(screenshot)
        self.save_shield_time(read)
        # self.open_shield_boost(screenshot)
        # self.save_use_shield_loc(screenshot)
        self.close(2)