#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# Imports
import logging

# ==============================================================================
def initLogger(logger, debug=False):
    format="%(name)-12s %(levelname)-7s: %(message)s" #%(module)-10s
    formatter = logging.Formatter(format)    
    ch = logging.StreamHandler()  
    ch.setFormatter(formatter)  
    logger.addHandler(ch)
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logger.setLevel(level)

def createAndInitLogger(name, debug=False):
    logger = logging.getLogger(name)
    initLogger(logger, debug)
    return logger

