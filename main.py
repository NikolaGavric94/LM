import cv2 as cv
import os
import keyboard
from windowcapture import WindowCapture
from vision import Vision
from housekeeping import Housekeeper
from bot import LMBot, BotState
from time import time
import easyocr

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their 
# own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False

# Initialize reader
reader = easyocr.Reader(['en'], gpu=True)
# initialize the WindowCapture class
wincap = WindowCapture('Lords Mobile')
# window offsets
window_offset = (wincap.offset_x, wincap.offset_y)
# initialize vision
vision = Vision(reader, window_offset)
# initialize Housekeeper
housekeeper = Housekeeper(vision)
# initialize bot
bot = LMBot(window_offset, (wincap.w, wincap.h), housekeeper)
# set of available bot commands
available_commands = ["#bal", "#start", "#end"]
# start threads
wincap.start()
bot.start()

while(True):
    # if we don't have a screenshot yet, don't run the code below this point yetc
    if wincap.screenshot is None:
        continue
    
    start = time()
    # update bot screenshot vision
    bot.update_screenshot(wincap.screenshot)

    # update the bot with the data it needs right now
    if bot.state == BotState.INITIALIZING:
        print ('Sleeping while being initialized...')
    elif bot.state == BotState.IDLE:
        pass
    elif bot.state == BotState.GATHERING_LOCATIONS:
        print ('Housekeeper started gathering locations')
        housekeeper.initialize(wincap.screenshot)
        print ('Housekeeper finished gathering locations')
        bot.state = BotState.IDLE
        print ('Bot going idle now')
    elif bot.state == BotState.APPLYING_SHIELD:
        print ('Being invaded, applying shield')
        bot.use_shield()
        print(f"--- Shielding took: {start - time():.2f} seconds ---")
        bot.open_shield_records()
        housekeeper.read_and_save_shield_timer(wincap.screenshot)
        print ('Shield expires at: %s' % (housekeeper.shield_expires_at.strftime("%d/%m/%Y %H:%M:%S")))
        bot.close(2)
        bot.state = BotState.CHECKING_SHIELD
    elif bot.state == BotState.CHECKING_SHIELD:
        # Is shield still active
        active = housekeeper.is_shield_active()
        print ('Shield is active? %s' % (active))
        if not active:
            bot.state = BotState.APPLYING_SHIELD
        else:
            print ('Shield timer expires at: %s' % (housekeeper.shield_expires_at.strftime("%d/%m/%Y %H:%M:%S")))
            bot.state = BotState.IDLE
    if DEBUG:
        # display the images
        cv.imshow('Matches', wincap.screenshot)
        key = cv.waitKey(1)
        if key == ord('q'):
            wincap.stop()
            bot.stop()
            cv.destroyAllWindows()
            break
        elif key == ord('a'):
            bot.state = BotState.CHECKING_SHIELD
print('Done.')