#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(c) L3i - Univ. La Rochelle
    joseph.chazalon (at) univ-lr (dot) fr

SmartDoc 2017 Sample Method

Processing module.
"""

# ==============================================================================
# Imports
import json
from collections import namedtuple

import cv2
import numpy as np

from utils.log import *
from trackers.SIFT_BFTracker import SIFT_BFTracker

# ==============================================================================
# Internal type definition
_Shape = namedtuple("Shape", ["x_len", "y_len"])
_Point = namedtuple("Point", ["x", "y"])

# ==============================================================================
class VideoCapture(object):
    '''
    Example processing class to produce a restored image given some video input.
    '''
    def __init__(self, debug=False, activate_gui=False):
        self._debug = debug
        self._logger = createAndInitLogger(__name__, debug)
        self._gui = activate_gui

    def _read_task_data(self, filename):
        '''
        Reads the `task_data.json` file and returns a tuple with
        all values.
        '''
        tmp = None
        with open(filename, "rb") as infile:
            tmp = json.load(infile)
        try:
            target_image_shape = _Shape(
                int(tmp["target_image_shape"]["x_len"]),
                int(tmp["target_image_shape"]["y_len"]))
            input_video_shape = _Shape(
                int(tmp["input_video_shape"]["x_len"]),
                int(tmp["input_video_shape"]["y_len"]))
            reference_frame_id = int(tmp["reference_frame_id"])
            object_coord_in_ref_frame = [
                _Point(float(tmp["object_coord_in_ref_frame"][name]["x"]),
                       float(tmp["object_coord_in_ref_frame"][name]["y"]))
                for name in 
                    ("top_left", "bottom_left", "bottom_right", "top_right")
                ]
        except KeyError, ValueError:
            msg = "'%s' is not a valid `task_data.json` file."
            self._logger.debug(msg)
            raise IOError(msg)
        self._logger.debug("Task data:")
        self._logger.debug("\ttarget_image_shape = %s" % str(target_image_shape))
        self._logger.debug("\tinput_video_shape = %s" % str(input_video_shape))
        self._logger.debug("\treference_frame_id = %s" % str(reference_frame_id))
        self._logger.debug("\tobject_coord_in_ref_frame = %s" % str(object_coord_in_ref_frame))
        return (target_image_shape, input_video_shape, 
                reference_frame_id, object_coord_in_ref_frame)

    def _check_vcap_is_ok(self, vcap_is_ok, current_frame_index):
        if not vcap_is_ok:
            raise IOError("Stream error in input video at frame %d." % current_frame_index)

    def _show_image(self, window, image):
        if self._gui:
            cv2.imshow(window, image)
            key_code = cv2.waitKey(20)
            if key_code & 0xff == ord('q'):
                raise KeyboardInterrupt()

    def _overlay_poly(self, image, poly):
        if self._gui:
            cv2.polylines(image, [np.int32(poly)], True, (0, 255, 0), 2)
            for name, pt in zip(("TL", "BL", "BR", "TR"), poly):
                cv2.putText(image, name, (int(pt[0]), int(pt[1])),
                    cv2.FONT_HERSHEY_PLAIN, 2, (64, 255, 64), 2)

    def process_video(self, task_data_path, video_path, 
                      reference_frame_path, output_path):
        '''
        This is the main function which processes a video capture and
        produces a restored image.
        In this example the video is processed in a single pass (in order
        to comply with what a real mobile application would probably
        have to do) and the blending is very naive.
        Perspective transform is estimated using keypoint matching
        with SIFT descriptors.
        '''
        # define windows names for GUI
        win_result = "Result Image"
        win_video = "Video Input"
        win_ref_frame = "Reference Frame"
        win_mask = "Blending Mask"
        if self._gui:
            for win in (win_result, win_video, win_ref_frame, win_mask):
                cv2.namedWindow(win, cv2.WINDOW_NORMAL)

        # define some variable(s) for the lazy
        logger = self._logger

        # open and parse task_data file
        task_data = self._read_task_data(task_data_path)
        (target_image_shape, input_video_shape, 
            reference_frame_id, object_coord_in_ref_frame) = task_data

        # open video file
        videocap = cv2.VideoCapture(video_path)
        frame_count = int(videocap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        frame_shape = _Shape(
                        int(videocap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)), 
                        int(videocap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))
        logger.debug("Input video informations:")
        logger.debug("\tframe_count = %s" % str(frame_count))
        logger.debug("\tframe_shape = %s" % str(frame_shape))

        # check task_data and video are consistent
        if frame_shape.x_len != input_video_shape.x_len or \
           frame_shape.y_len != input_video_shape.y_len:
           raise IOError("Frame shapes of task data and video are not consistent.")
        if frame_count <= reference_frame_id:
            raise IOError("Reference frame id is out of range for video.")

        # prepare output structure (we could read and copy reference frame instead)
        result_image = np.zeros(target_image_shape, dtype=np.float32)

        # read first frame
        current_frame_index = 0
        vcap_is_ok, current_frame = videocap.read()
        self._check_vcap_is_ok(vcap_is_ok, current_frame_index)

        # discard frames until we are on the reference frame (0-indexed)
        while current_frame_index < reference_frame_id:
            logger.info("Skipping frame %d" % current_frame_index)
            vcap_is_ok, current_frame = videocap.read()
            current_frame_index += 1
            self._check_vcap_is_ok(vcap_is_ok, current_frame_index)
            self._show_image(win_video, current_frame)

        # prepare polygons for object and target
        object_poly = np.float32(object_coord_in_ref_frame)
        target_poly = np.float32([[0, 0],
                               [0, target_image_shape.y_len-1],
                               [target_image_shape.x_len-1, target_image_shape.y_len-1],
                               [target_image_shape.x_len-1, 0]])

        # store copy of reference frame
        reference_frame = current_frame.copy()

        # draw contour and display
        self._overlay_poly(current_frame, object_poly)
        self._show_image(win_ref_frame, current_frame)

        # warp reference frame into target image
        trans = cv2.getPerspectiveTransform(object_poly, target_poly)
        result_image = cv2.warpPerspective(reference_frame, trans, result_image.shape)
        self._show_image(win_result, result_image)

        # (naive) create a simple SIFT tracker to project frames
        # Note: There may be better techniques to estimate the relative position
        # between the camera and the document, or the position between the 
        # reference frame and the current frame.
        logger.debug("Creating tracker.")
        tracker = SIFT_BFTracker(debug=self._debug)
        logger.debug("Reinitializing tracker with frame size (w=%.3f; h=%.3f)" 
            % (frame_shape.x_len, frame_shape.y_len))
        tracker.reinitFrameSize(frame_shape.x_len, frame_shape.y_len)
        logger.debug("Configuring tracker's model")
        tracker.reconfigureModel(result_image)
        logger.debug("Tracker configuration complete.")

        # iterate over video frames
        while True:
            vcap_is_ok, current_frame = videocap.read()
            if not vcap_is_ok:
                logger.debug("End of stream reached after frame %d" % current_frame_index)
                # end of stream reached
                break
            current_frame_index += 1
            current_frame_orig = current_frame.copy()

            # find the object
            (rejected, tl, bl, br, tr) = tracker.processFrame(current_frame_orig)
            if not rejected:
                logger.info("frame %03d: A tl:(%-4.2f,%-4.2f) bl:(%-4.2f,%-4.2f) "
                                     "br:(%-4.2f,%-4.2f) tr:(%-4.2f,%-4.2f)" 
                            %(current_frame_index, 
                                tl[0], tl[1], bl[0], bl[1], br[0], br[1], tr[0], tr[1]))
                self._overlay_poly(current_frame, [tl, bl, br, tr])
            else:
                logger.info("frame %03d: R" % current_frame_index)
                if self._gui:
                    cv2.circle(current_frame, (frame_shape.x_len/2, frame_shape.y_len/2), 
                        20, (0, 0, 255), 10)
            self._show_image(win_video, current_frame)
            
            # blend object region directly into result image
            if not rejected:
                object_poly = np.float32([tl, bl, br, tr])
                trans = cv2.getPerspectiveTransform(object_poly, target_poly)
                frame_poly = np.float32([[0, 0],
                               [0, frame_shape.y_len-1],
                               [frame_shape.x_len-1, frame_shape.y_len-1],
                               [frame_shape.x_len-1, 0]])   

                mask = np.zeros(result_image.shape, dtype=np.uint8)
                result_roi = cv2.perspectiveTransform(
                    frame_poly.reshape(1, -1, 2), 
                    trans, 
                    (target_image_shape.y_len,target_image_shape.x_len)
                    ).reshape(-1, 2)
                result_roi = np.int32(result_roi)
                white = (255,255,255) 
                cv2.fillPoly(mask, [result_roi], white)
                self._show_image(win_mask, mask)
                pre_result = cv2.warpPerspective(
                    current_frame_orig, 
                    trans, 
                    (result_image.shape[1],result_image.shape[0]))
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # NOTE: changing the following line might be the easiest
                # way to improve this naive implementation. Here we
                # merely copy the content of the current frame over the
                # result image, overwriting previous pixel without any
                # weighting, discarding, color correction, perspective 
                # adjustment, border fading, etc.
                # There are, of course, many other possible improvements
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                np.copyto(result_image, pre_result, where=(mask>0)) # !!!!!!!!!!
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            self._show_image(win_result, result_image)

        # write output
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # NOTE: you may want to improve the contrast of the image here, as
        # it will be compared against an image generated from the digital 
        # source. Beware of not introducing noise at it will penalize your 
        # results.
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        cv2.imwrite(output_path, result_image)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        logger.debug("Wrote result image to '%s'." % output_path)
        
        logger.info("Process complete.")
        # wait until user quits if GUI is active
        if self._gui:
            # Wait for key press at the end of the process.
            logger.info("Please press any of the following keys to exit:")
            logger.info("\t SPACE, ESC, Q, ENTER")
            should_quit = False
            exit_keys = [32, 27, ord('q'), 13]
            while not should_quit:
                key_code = cv2.waitKey(100) & 0xff
                should_quit = key_code in exit_keys
        logger.debug("VideoCapture end.")
    # / VideoCapture.process_video()
