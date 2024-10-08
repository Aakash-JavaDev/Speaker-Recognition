#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# File: LPC.py
# Date: Thu Mar 19 19:37:11 2015 +0800


import time
import numpy as np  
#import scikits.talkbox as tb
# from scikits.talkbox.linpred import levinson_lpc
from numpy import *
from scipy.io import  wavfile
from .MFCC import hamming
from .utils import cached_func, diff_feature
from spafe.features.lpc import lpcc

class LPCExtractor(object):
    def __init__(self, fs, win_length_ms, win_shift_ms, n_lpc,
                 pre_emphasis_coef):
        self.PRE_EMPH = pre_emphasis_coef
        self.n_lpc = n_lpc
        #self.n_lpcc = n_lpcc + 1

        self.FRAME_LEN = int(float(win_length_ms) / 1000 * fs)
        self.FRAME_SHIFT = int(float(win_shift_ms) / 1000 * fs)
        self.window = hamming(self.FRAME_LEN)


    def lpc_to_cc(self, lpc):
        lpcc = zeros(self.n_lpcc)
        lpcc[0] = lpc[0]
        for n in range(1, self.n_lpc):
            lpcc[n] = lpc[n]
            for l in range(0, n):
                lpcc[n] += lpc[l] * lpcc[n - l - 1] * (n - l) / (n + 1)
        for n in range(self.n_lpc, self.n_lpcc):
            lpcc[n] = 0
            for l in range(0, self.n_lpc):
                lpcc[n] += lpc[l] * lpcc[n - l - 1] * (n - l) / (n + 1)
        return -lpcc[1:]

    def lpcc(self, signal):
        # lpc = levinson_lpc.lpc(signal, self.n_lpc)[0]
        # return lpc[1:]
        lpcc = self.lpc_to_cc(lpc)
        return lpcc

    def extract(self, signal):
        frames = (len(signal) - self.FRAME_LEN) // self.FRAME_SHIFT + 1
        feature = []
        for f in range(0,frames):
            frame = signal[f * self.FRAME_SHIFT : f * self.FRAME_SHIFT +
                           self.FRAME_LEN] * self.window
            frame[1:] -= frame[:-1] * self.PRE_EMPH
            feature.append(self.lpcc(frame))

        feature = array(feature)
        feature[isnan(feature)] = 0
        return feature

@cached_func
def get_lpc_extractor(fs, win_length_ms=32, win_shift_ms=16,
                       n_lpc=15, pre_emphasis_coef=0.95):
    ret = LPCExtractor(fs, win_length_ms, win_shift_ms, n_lpc, pre_emphasis_coef)
    return ret


def extract_lpc(fs, signal=None, diff=False, **kwargs):
    """accept two argument, or one as a tuple"""
    if signal is None:
        assert type(fs) == tuple
        fs, signal = fs[0], fs[1]
    signal = np.array(signal,dtype = np.float32)
    print(signal)
    signal = np.expand_dims(signal,axis = -1)
    print("Signal in LPC: ",fs,signal.shape)
    from spafe.utils.preprocessing import SlidingWindow
    result_lpc = lpcc(sig=signal,fs = fs,window=SlidingWindow(0.032,0.016,"hamming"),
                       order=15, pre_emph_coeff=0.95,pre_emph=True)
    # ret = get_lpc_extractor(fs, **kwargs).extract(signal)
    # if diff:
    #     return diff_feature(ret)
    # return ret
    return result_lpc

if __name__ == "__main__":
    extractor = LPCCExtractor(8000)
    fs, signal = wavfile.read("../corpus.silence-removed/Style_Reading/f_001_03.wav")
    start = time.time()
    ret = extractor.extract(signal)
    print (len(ret))
    print (len(ret[0]))
    print (time.time() - start)
