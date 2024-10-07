


#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# File: __init__.py
# Date: Sat Nov 29 21:42:15 2014 +0800


import sys
from .MFCC import *
from .LPC import extract_lpc
import numpy as np

def get_extractor(extract_func, **kwargs):
    def f(tup):
        return extract_func(*tup, **kwargs)
    return f

def mix_feature(tup):
    mfcc = extract(signal=tup[1],fs = tup[0])
    lpc = extract_lpc(signal=tup[1],fs = tup[0])
    if len(mfcc) == 0:
        print >> sys.stderr, "ERROR.. failed to extract mfcc feature:", len(tup[1])
    concat_result = np.concatenate((mfcc, lpc), axis=1)
    print(concat_result.shape)
    return concat_result
