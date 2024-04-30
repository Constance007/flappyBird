import cv2
import cvzone
import numpy as np
import pyautogui
from cvzone.ColorModule import ColorFinder

def caputure_screen_region_opencv(x, y, desired_width, desired_height):
    screenshot = pyautogui.screenshot(region=(x, y, desired_width, desired_height))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot


def pre_process(_imgCrop):
    gray_frame = cv2.cvtColor(_imgCrop, cv2.COLOR_BGR2GRAY)
    _, binary_frame = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY_INV)
    canny_frame = cv2.Canny(binary_frame, 50, 50)
    kernel = np.ones((5, 5))
    dilated_frame = cv2.dilate(canny_frame, kernel, iterations=1)
    return dilated_frame


def flappy_location(img):
    hsVals = {'hmin': 0, 'smin': 145, 'vmin': 101, 'hmax': 40, 'smax': 255, 'vmax': 255}  # Flappy
    myColor, mask = myColorFinder.update(img, hsVals)
    imgContours, contours = cvzone.findContours(myColor, mask, minArea=100)

    center = [0, 0]
    if len(contours) > 0:
        center = contours[0]['center']

    # print(center[1])
    return imgContours, center[0], center[1]


def spacebar(flappy_y, near_obstacle_course):
    if near_obstacle_course is False:
        if flappy_y > 400:
            pyautogui.press("space")
        else:
            pass


def game_logic(_imgCrop, _imgPre, flappy_xLoc, flappy_yLoc, near_obstacle_course, press):
    imgContours, conFound = cvzone.findContours(_imgCrop, _imgPre, minArea=100, filter=None)

    # Pipe detected
    if len(conFound) > 0:
        near_obstacle_course = True
        imgContours = detect_pipe(conFound, imgContours, flappy_yLoc, flappy_xLoc, press)

        # # Pipe coming down from above
        # if pipe_y == 0:
        #     # Flight is below pipe's end
        #     if (flappy_yLoc > pipe_y + pipe_h + 50):
        #         #Able to fly between pipes
        #         if (flappy_yLoc < pipe_y + pipe_h + 300):
        #             print("Maintain height - press spacebar | pipe's len:", pipe_y + pipe_h, "| flappy: ", flappy_yLoc)
        #         else:
        #             # pyautogui.press("space")
        #             pass
        #
        #     # Flight is too high
        #     else:
        #         print("Flight too high")

        # Pipe is coming up from below
        # else:

    return imgContours, near_obstacle_course


def detect_pipe(conFound, imgContours, flappy_yLoc, flappy_xLoc, press):
    if len(conFound) > 0:
        if len(conFound) > 1:
            # imgContours = detect_pipes(conFound, imgContours)
            pass

        sorted_conFound = sorted(conFound, key=lambda x: x["bbox"][0])
        # Obtain first bounding box
        bbox = sorted_conFound[0]["bbox"]
        pipe_x, pipe_y, pipe_w, pipe_h = bbox
        cv2.rectangle(imgContours, (pipe_x, pipe_y), (pipe_x + pipe_w, pipe_y + pipe_h), (0, 255, 0), 2)  # CALIBRATION
        # print("1 PIPE --- pipe's y_loc:", pipe_y , "| flappy's y_Loc: ", flappy_yLoc) # CALIBRATION
        # print("1 PIPE --- pipe's y_loc:", pipe_y + pipe_h   , "| flappy's y_Loc: ", flappy_yLoc) # CALIBRATION
        print("Flappy x-", flappy_xLoc, " | Pipe x-", pipe_x + pipe_w, "| Flappy y-", flappy_yLoc, "| Pipe y-",
              pipe_y + pipe_h)  # CALIBRATION

        direction = pipe_direction(pipe_y)
        # Pipe is coming down from the sky
        if direction:
            pyautogui.press("space")

        # Flappy is in front of pipe
        else:

            while flappy_xLoc < pipe_x + pipe_w:
                print("FRONT ")
                if flappy_yLoc > pipe_y + pipe_h + 170:
                    # print("FRONT -- press", flappy_yLoc, " ", pipe_y + pipe_h)
                    pyautogui.press("space")

                return imgContours

            bbox2 = sorted_conFound[1]["bbox"]
            x, y, w, h = bbox2
            cv2.rectangle(imgContours, (x, y), (x + w, y + h), (0, 255, 0), 2)  # CALIBRATION

            print("BTW    -- press", flappy_yLoc, " ", pipe_y + pipe_h, " ", y + h)
            if flappy_yLoc > pipe_y + pipe_h + 170 and flappy_yLoc < y + h + 5:
                pyautogui.press("space")
                                                           
            # # Flappy is in front of pipe
            # if flappy_xLoc < pipe_x + pipe_w:
            #     if flappy_yLoc > pipe_y + pipe_h + 170:
            #         print("FRONT -- press", flappy_yLoc, " ", pipe_y + pipe_h)
            #         pyautogui.press("space")
            #
            # # Flappy is inbetween pipes
            # if flappy_xLoc > pipe_x + pipe_w:
            #     if flappy_yLoc > pipe_y + pipe_h + 170:
            #         print("BTW    -- press", flappy_yLoc, " ", pipe_y + pipe_h)
            #         pyautogui.press("space")
            #
            #     else:
            #         pass

    return imgContours


# def detect_pipes(conFound, imgContours):
#     sorted_conFound = sorted(conFound, key=lambda x: x["bbox"][0])
#
#     # Obtain first bounding box
#     bbox = sorted_conFound[0]["bbox"]
#     pipe_x, pipe_y, pipe_w, pipe_h = bbox
#     cv2.rectangle(imgContours, (pipe_x, pipe_y), (pipe_x + pipe_w, pipe_y + pipe_h), (0, 255, 0), 2)  # CALIBRATION
#
#     bbox2 = sorted_conFound[1]["bbox"]
#     x, y, w, h = bbox2
#     cv2.rectangle(imgContours, (x, y), (x + w, y + h), (0, 255, 0), 2) # CALIBRATION
#     print("2 PIPES --- Pipe #1:", pipe_y + pipe_h, "| Pipe #2: ", y + h,"| Flappy: ", flappy_yLoc )
#     return imgContours

def pipe_direction(pipe_y):
    # False - Pipe is coming down from above
    # True - Pipe is coming up from below
    # print(pipe_y )
    if pipe_y == 0:
        return False
    return True


myColorFinder = ColorFinder(False)
obstacle_course = False
press = False
while True:
    # Capture the screen region of the game
    # imgGame = caputure_screen_region_opencv(380, 0, 480, 700) #pos1
    imgGame = caputure_screen_region_opencv(50, 0, 480, 700)  # pos2*

    # Crop the image to the desired region
    cp = 110, 660, 260
    # cp = 110, 500, 270
    imgCrop = imgGame[cp[0]:cp[1], cp[2]:]

    # Preprocess the image
    imgPre = pre_process(imgCrop)

    # Find flappy
    imgContours, flappy_xLoc, flappy_yLoc = flappy_location(imgGame)

    # Find pipes
    spacebar(flappy_yLoc, obstacle_course)

    contoursImg, obstacle_course = game_logic(imgCrop, imgPre, flappy_xLoc, flappy_yLoc, obstacle_course, press)
    # cv2.circle(imgGame, (flappy_xLoc, flappy_yLoc), 10, (255, 0, 0), cv2.FILLED)


    #cv2.imshow("Game", imgGame)
    # cv2.imshow("imgCrop", imgCrop)
    # cv2.imshow("imgPre", imgPre)
    # cv2.imshow("imgContours", imgContours)
    cv2.imshow("contours", contoursImg)  # Check position

    cv2.waitKey(1)
