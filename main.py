import cv2 as cv
import os
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

DEBUG = True

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
        bot.open_shield_boost()
        bot.use_shield()
        print(f"--- Shielding took: {start - time():.2f} seconds ---")
        housekeeper.open_and_save_shield_timer(wincap.screenshot)
        print ('Shield expires at: %s' % (housekeeper.shield_expires_at.strftime("%d/%m/%Y %H:%M:%S")))
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
    # elif bot.state == BotState.IDLE:
    #     if vision.is_chat_open(wincap.screenshot):
    #         print ('Searching for keywords now')
    #         text = reader.readtext(wincap.screenshot)
    #         for t in text:
    #             box, text, accuracy = t
    #             if accuracy >= 0.99:
    #                 print (text, accuracy)
    #                 cv.rectangle(wincap.screenshot, box[0], box[2], (0, 255, 0), 2)

    #     else:
    #         print ('Opening chat')
    #         keyboard.press('c')
    #         keyboard.release('c')
    #         print ('Searching for keywords now')
    #         pass
    # elif bot.state == UserAction.CHECK_BALANCE:
    #     print ('checking balancen ow')

    # cv.imshow('Matches', wincap.screenshot)
    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    key = cv.waitKey(1)
    if key == ord('q'):
        wincap.stop()
        bot.stop()
        cv.destroyAllWindows()
        break
print('Done.')
