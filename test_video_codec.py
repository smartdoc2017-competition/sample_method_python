#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(c) L3i - Univ. La Rochelle
    joseph.chazalon (at) univ-lr (dot) fr

SmartDoc 2017 Sample Method

This is a simple test program which plays a given video in a window if
OpenCV has the support for reading such file. It fails otherwise.
"""

# ==============================================================================
# Imports
import argparse
import os
import os.path
import sys

import cv2
# ==============================================================================
# Constants
PROG_VERSION = "1.0"
PROG_NAME = "SD17-codec-test"
PROG_DESCRIPTION = "SmartDoc 2017 Sample Method - codec test for video input"
EXITCODE_OK = 0
EXITCODE_KBDBREAK = 10
EXITCODE_IOERROR = 20
EXITCODE_UNKERR = 254

DBGLINELEN = 80
DBGSEP = "-"*DBGLINELEN

# ==============================================================================
# ==============================================================================
class Application(object):
    '''Main application class.'''

    def main(self):
        '''Public main function.'''
        # Parse args
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description=PROG_DESCRIPTION, 
            version=PROG_VERSION)
        parser.add_argument('video', 
            help='Path to `input.mp4` file.')
        args = parser.parse_args()
        # Print info
        print "Test codec for file '%s'" % args.video
        try:
            win_video = "Video"
            cv2.namedWindow(win_video, cv2.WINDOW_NORMAL)
            print "Starting display, press <q> to quit."
            videocap = cv2.VideoCapture(args.video)
            status, current_frame = videocap.read()
            frame_count = 1
            # Display loop
            while status:
                print "Got frame %03d" % frame_count
                cv2.imshow(win_video, current_frame)
                key_code = cv2.waitKey(40)
                if key_code & 0xff == ord('q'):
                    raise KeyboardInterrupt()
                status, current_frame = videocap.read()
                frame_count += 1
            print "End of stream reached at frame %03d" % frame_count
            print "Processing complete."
            return EXITCODE_OK
        except KeyboardInterrupt:
            print "Process interrupted by user."
            return EXITCODE_KBDBREAK
        except IOError as e:
            print "Problem in reading or writing file."
            print e
            return EXITCODE_IOERROR
        except e:
            print "Unknown error."
            print e
            return EXITCODE_UNKERR

# ==============================================================================
if __name__ == "__main__":
    res = Application().main()
    if res is not None:
        sys.exit(res)



