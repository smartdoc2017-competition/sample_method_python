#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# Imports
from collections import namedtuple

import cv2

from utils.log import *

# ==============================================================================
def multiPyrDown(img, num_pyrdown=1):
    res = img
    for q in range(num_pyrdown):
        res = cv2.pyrDown(res)
    return res

# ==============================================================================
class Tracker(object):
    """
    Object tracking API + a few utility methods.
    """
    # Interface
    # --------------------------------------------------------------------------

    def reconfigureModel(self, model_image):
        """
        Tracker x numpy.array ---> None
        Will be called once before processing each test sequence with the appropriate
        model of the object to track.
        """
        pass

    def reinitFrameSize(self, frame_width, frame_height):
        """
        Tracker x int x int ---> None
        Will be called once before processing each test sequence with the appropriate
        size of the image frames which will be provided.
        """
        self.frame_width = frame_width
        self.frame_height = frame_height


    def processFrame(self, frame_image):
        """
        Tracker x np.array ---> tuple(rejected:bool, tl:Pt, bl:Pt, br:Pt, tr:Pt)
        Will be called once with each frame to process.
        You MUST override this method in child class.

        Frame data may contain more than raw image data.
        """
        raise NotImplementedError()

    # Utility methods
    # --------------------------------------------------------------------------
    def __init__(self, 
                 num_pyrdown_model=0,
                 num_pyrdown_frames=0,
                 debug=False):
        self._logger = createAndInitLogger(__name__, debug)

        self._num_pyrdown_model  = num_pyrdown_model
        self._num_pyrdown_frames = num_pyrdown_frames


    def _autoPyrDownModel(self, img):
        return multiPyrDown(img, self._num_pyrdown_model)

    def _autoPyrDownFrame(self, img):
        return multiPyrDown(img, self._num_pyrdown_frames)
            
    def _scaleCoord(self, coord):
        return coord * 2**self._num_pyrdown_frames


