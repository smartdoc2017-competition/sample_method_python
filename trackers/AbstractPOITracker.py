#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(c) L3i - Univ. La Rochelle
    joseph.chazalon (at) univ-lr (dot) fr

SmartDoc 2017 Sample Method

Tracking tools.
"""

# ==============================================================================
# Imports
import cv2
import numpy as np

from utils.log import *
from Tracker import *

# ==============================================================================
class AbstractPOITracker(Tracker):
    '''
    Abstract class for object tracking using keypoints and local descriptors.
    '''
    def __init__(self, detector, matcher,
                 num_pyrdown_model=0,
                 num_pyrdown_frames=0,
                 num_of_matches=15,
                 second_match_tresh=0.75,
                 debug=False):
        super(AbstractPOITracker, self).__init__(
                num_pyrdown_model=num_pyrdown_model,
                num_pyrdown_frames=num_pyrdown_frames,
                debug=debug)
        self._logger = createAndInitLogger(__name__, debug)

        self.detector = detector
        self.matcher = matcher
        self.num_of_matches = num_of_matches
        self.second_match_tresh = second_match_tresh

    def reconfigureModel(self, model_image):
        # Clears the train descriptor collection.
        self.matcher.clear()

        Cimg = model_image
        Cimg = self._autoPyrDownModel(Cimg)
        Cgray = cv2.cvtColor(Cimg, cv2.COLOR_BGR2GRAY)
        (xmax, ymax) = (Cimg.shape[1], Cimg.shape[0])
        tl = (1, 1)
        bl = (1, ymax)
        br = (xmax, ymax)
        tr = (xmax, 1)
        self.mdl_quad = np.float32([tl, bl, br, tr])
        # print Cquad
        (Ckeyp,Cdesc) = self.detector.detectAndCompute(Cgray,None)
        # self.matcher.add(np.uint8([Cdesc]))
        self.matcher.add([Cdesc])
        self.mdl_keyp = Ckeyp

    def processFrame(self, frame_image):
        rejectCurrent = True
        tl = None
        bl = None
        br = None
        tr = None
        img = frame_image

        img = self._autoPyrDownFrame(img)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        (keypoints,descriptors) = self.detector.detectAndCompute(gray,None)
        if descriptors is None:
            self._logger.debug("R no descriptors")
        else:
            matches = self.matcher.knnMatch(descriptors, k = 2)
            matches = [m[0] for m in matches if len(m) >= 2 and m[0].distance < m[1].distance * self.second_match_tresh]
            if len(matches) < self.num_of_matches:
                self._logger.debug("R: not enough matches (%d < %d)", len(matches), self.num_of_matches)
            else:
                pt00 = [self.mdl_keyp[m.trainIdx].pt for m in matches]
                pt10 = [keypoints[m.queryIdx].pt for m in matches]
                pt0, pt1 = np.float32((pt00, pt10))
                H, s = cv2.findHomography(pt0, pt1, cv2.RANSAC, 3.0)

                s = s.ravel() != 0
                if s.sum() < self.num_of_matches:
                    self._logger.debug("R: not enough RANSAC inliers (%d < %d, got %d matches before)", s.sum(), self.num_of_matches, len(matches))
                else:
                    pt0, pt1 = pt0[s], pt1[s]
                    q = cv2.perspectiveTransform(self.mdl_quad.reshape(1, -1, 2), H).reshape(-1, 2)

                    rejectCurrent = False
                    tl = (self._scaleCoord(q[0][0]), self._scaleCoord(q[0][1]))
                    bl = (self._scaleCoord(q[1][0]), self._scaleCoord(q[1][1]))
                    br = (self._scaleCoord(q[2][0]), self._scaleCoord(q[2][1]))
                    tr = (self._scaleCoord(q[3][0]), self._scaleCoord(q[3][1]))
                    
        return (rejectCurrent, tl, bl, br, tr)
