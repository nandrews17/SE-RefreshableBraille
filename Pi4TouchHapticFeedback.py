# nandrews17@georgefox.edu, ...
# Software Engineering - Refreshable 'Braille'
# 2020-03-04

import cv2
import time
import threading
import traceback
import numpy as np
import RPi.GPIO as GPIO


# Global Variables (can/some will be overwritten)
mouse = [-1, -1]
motor = 16
fileName = 'NULL'
displaying = False
giveMouseFeedback = False
img = np.zeros((100, 100, 100), np.uint8)
grayscale = np.zeros((100, 100, 100), np.uint8)

# main method for Refreshable Braille Software for Pi4
def main():
    global img
    global grayscale
    global fileName

    startupMessage()

    while True:
        try:
            # Choses the JPEG, PNG, ETC. image to analyze or exit if user wants
            fileName = input('Enter file name [\'e\' or \'exit\' to quit]: ')
            if (checkForExit(fileName) != 0):
                break

            # Incorperates OpenCV to read the image file and assign width and height
            img = cv2.imread(fileName, 1)
            width = img.shape[1]
            height = img.shape[0]
            print('\n\''+fileName+'\' FOUND')

            # Enters resizing function for image if desired and gets grayscale of final image
            resizeOption = input('Resize image? [y/n] ')
            if (resizeOption == 'y') | (resizeOption == 'Y'):
                img = resizeImage(width, height)
            grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            displayForBrailleFeedback()

        # Catches and displays exceptions then restarts loop
        except Exception:
            print('\nERROR:\n' + traceback.format_exc())


# Prints the startup message
def startupMessage():
    print('SE Refreshable Braille Project-version2.2\nENGR381')
    print('  1. Make sure an image is in same file.\n  2. Type desired image name right.')
    print('    -Name And Type Required (*.png, *.jpg, *.tiff, etc.).')
    print('    -Example: heart.png\n')


# Checks for user input to exit
def checkForExit(i):
    exitValue = 0
    if (i == 'EXIT') | (i == 'exit') | (i == 'e') | (i == 'E'):
        exitValue = 1
    return exitValue


# Rescaling (X & Y Axis) [MAY BE TEMPORARY FEATURE FOR TESTING]
def resizeImage(imageWidth, imageHeight):
    optionChosen = False
    while optionChosen == False:
        pixelScale = input('Enter desired 2D width/height pixelation [100-1000]: ')
        if not pixelScale.isdigit():
            print('\nERROR: Invalid input')
        elif (int(pixelScale) < 100) | (int(pixelScale) > 1000):
            print('\nERROR: Invalid input')
        else:
            pixelScale = int(pixelScale)
            optionChosen = True

    # Resizes image using scale factor received
    if imageWidth > imageHeight:
        scaleFactor = 1-((imageWidth-pixelScale)/imageWidth)
    else:
        scaleFactor = 1-((imageHeight-pixelScale)/imageHeight)
    imageWidth = int(imageWidth * scaleFactor)
    imageHeight = int(imageHeight * scaleFactor)
    dim = (imageWidth, imageHeight)

    return cv2.resize(img, dim, interpolation = cv2.INTER_AREA)


# Display the final image and incorporate mouse event capture
def displayForBrailleFeedback():
    global displaying
    # Option to display either grayscale or original version of image for testing
    optionChosen = False
    while optionChosen == False:
        imageOption = input('Grayscale or Original? [g/o]: ')
        if (imageOption == 'G') | (imageOption == 'g'):
            cv2.imshow(fileName, grayscale)
            optionChosen = True
        elif (imageOption == 'O') | (imageOption == 'o'):
            cv2.imshow(fileName, img)
            optionChosen = True
        else:
            print('\nERROR: Invalid input')
    # Start both the thread for detecting user interaction and GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(motor, GPIO.OUT)
    displaying = True
    thread = threading.Thread(target=threadFunction, args=(), daemon=True)
    thread.start()
    # Calls mouse callback function to capture mouse events until image closes
    cv2.setMouseCallback(fileName, mouseFunction)
    cv2.waitKey(0)
    displaying = False
    cv2.destroyAllWindows()
    GPIO.cleanup()


# Captures mouse events and can be configured to output image values various ways
def mouseFunction(event, x, y, flags, params):
    global giveMouseFeedback
    global mouse

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse = [x, y]
        giveMouseFeedback = True

    elif event == cv2.EVENT_MOUSEMOVE and giveMouseFeedback:
        mouse = [x, y]

    elif event == cv2.EVENT_LBUTTONUP:
        giveMouseFeedback = False


# Gives feedback based on mouseFunction method and mouse's position
def feedbackFunction(x, y):
    if y > -1 and y < img.shape[0] and x > -1 and x < img.shape[1]:
        if grayscale[y, x] < 128 and giveMouseFeedback == True:
            GPIO.output(motor, 1)
        else:
            GPIO.output(motor, 0)


# Thread for feedback looping on mouse function and callback
def threadFunction():
    while displaying == True:
        feedbackFunction(mouse[0], mouse[1])


main()
