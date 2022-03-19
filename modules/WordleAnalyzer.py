import cv2
import numpy as np
import math
import datetime

import glob
import os

class WordleAnalyzer:

    def __init__ (self, todate=None):
        if todate == None:
            todate = datetime.datetime.now().date().isoformat()
        self.TODATE = todate

    def OpenFile (self):
        self.IMAGE = cv2.imread(f"./images/{self.TODATE}.png")

    def CropImage (self, img):
        center_x, center_y = img.shape[1] / 2, img.shape[0] / 2

        width_scaled, height_scaled = img.shape[1] * 0.5, img.shape[0] * 0.85
        left_x, right_x = center_x - width_scaled / 2, center_x + width_scaled / 2
        top_y, bottom_y = center_y - height_scaled / 2, center_y + (center_y - height_scaled / 2.8)
    
        self.CROPPED = img[int(top_y):int(bottom_y), int(left_x):int(right_x)]

        return self.CROPPED

    def FindColor(self, img, lower, upper):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)

        return mask

    def FindYellows (self, img):
        lower_bound = np.array([25,50,50])   
        upper_bound = np.array([32,255,255])
        
        return self.FindColor(img, lower_bound, upper_bound)

    def FindGreens (self, img):
        lower_bound = np.array([36, 50, 70])   
        upper_bound = np.array([89, 255, 255])
        
        return self.FindColor(img, lower_bound, upper_bound)

    def FindCenters (self, img):
        # Finds centers of non matches (non matches are sent as img)
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        CenterPoints = []
        for contour in contours:
            area = cv2.contourArea(contour)

            epsilon = .1 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if not approx.shape[0] == 4:
                continue
            else:
                lenA = max(max(abs(approx[0] - approx[1])))
                lenB = max(max(abs(approx[1] - approx[2])))
                lenC = max(max(abs(approx[2] - approx[3])))

                if not (lenA == lenB and lenB == lenC):
                    continue
            
            # X1, Y1 = approx[0]  
            minX, maxX = None, None
            minY, maxY = None, None

            for point in approx:
                x = point[0][0]
                y = point[0][1]

                if maxX == None or x > maxX:
                    maxX = x
                
                if minX == None or x < minX:
                    minX = x

                if maxY == None or y > maxY:
                    maxY = y
                
                if minY == None or y < minY:
                    minY = y
            
            centerX = (maxX - minX) + minX
            centerY = (maxY - minY) + minY
            CenterPoints.append( (centerX, centerY) )

        return CenterPoints
    
    def MakeBoard (self):
        board = cv2.imread("./images/base.png")
        Cropped = self.CropImage (board)

        cv2.imwrite(f"./images/board_2.png", Cropped)

    def Cleanup (self, path="./images/"):
        files = glob.glob(f'./images/*')

        for _file in files:
            if not ".png" == _file[-4:]:
                continue

            if not f"{self.TODATE}.png" in _file:# and (not 'base' in _file and 'board' in _file):
                os.remove(_file)


    def RunAttempt (self, initial=False):
        Original = cv2.imread(f"./images/{self.TODATE}.png")
        
        if initial:
            board = cv2.imread("./images/board_2.png")
        else:
            board = cv2.imread(f"./images/{self.TODATE}_PREV.png")

        Cropped = self.CropImage (Original)

        # print (f'Sizes: [{Cropped.shape}] | [{board.shape}] || {Original.shape}')
        attemptDifference = cv2.absdiff(Cropped, board)

        grayDifference = cv2.cvtColor(attemptDifference, cv2.COLOR_BGR2GRAY)
        binaryDifference = cv2.threshold(grayDifference, 5, 255, cv2.THRESH_BINARY)[1]

        YellowMask = self.FindYellows(attemptDifference)
        GreenMask = self.FindGreens(attemptDifference)


        CentersOfAll = self.FindCenters(binaryDifference)

        assert len(CentersOfAll) != 0, 'No centers found; to start from.'

        NonYellows  = cv2.absdiff(binaryDifference, YellowMask)
        NonGreens   = cv2.absdiff(binaryDifference, GreenMask)


        CentersOfNonYellows = self.FindCenters(NonYellows)
        CentersOfNonGreens = self.FindCenters(NonGreens)

        TruePositions = [val[0] for val in CentersOfAll]
        TruePositions.sort()

        YellowIndex = []
        GreenIndex = []

        if not len(CentersOfAll) == len(CentersOfNonYellows):
            for i, center in enumerate(CentersOfAll):
                if not center in CentersOfNonYellows:
                    YellowIndex.append(TruePositions.index(center[0]))
        
        if not len(CentersOfAll) == len(CentersOfNonGreens):
            for i, center in enumerate(CentersOfAll):
                if not center in CentersOfNonGreens:
                    GreenIndex.append(TruePositions.index(center[0]))

        # print (f"Yellows: {YellowIndex}")      
        # print (f"Greens: {GreenIndex}")    
          
        # print (f"All: {CentersOfAll}")      
        # print (f"NonYellows: {CentersOfNonYellows}")      
        # print (f"NonGreens: {CentersOfNonGreens}")      

        cv2.imwrite(f"./images/{self.TODATE}_PREV.png", Cropped)

        return YellowIndex, GreenIndex


