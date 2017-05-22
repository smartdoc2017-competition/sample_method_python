#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# Imports
import cv2

from utils.log import *
from AbstractPOITracker import *

# ==============================================================================
class SIFT_BFTracker(AbstractPOITracker):
    def __init__(self, debug=False):
        detector = cv2.SIFT(nfeatures=0,
                            nOctaveLayers=10,
                            contrastThreshold=0.04,
                            edgeThreshold=10.0,
                            sigma=1.6)
        matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

        super(SIFT_BFTracker, self).__init__(detector, 
                                          matcher, 
                                          num_pyrdown_model=0, 
                                          num_of_matches=15,
                                          debug=debug)

        self._logger = createAndInitLogger(__name__, debug)

