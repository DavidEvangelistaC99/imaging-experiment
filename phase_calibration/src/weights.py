# Weights module to not affect the overdetereminated LS
import numpy
'''
(0,1) -> 0
(0,2) -> 1
(0,3) -> 2 ...
(1,2) -> 7 ...
'''

def get_weights(mode, N):
    w = numpy.ones(N)

    if mode == 1: # Imaging ESF - 2026_03
        w[[0]] = 0.1
        w[[2,3]] = 0.2
        w[[4]] = 0.5
        w[[5]] = 0.1
        w[[7,8,9,10,11,12]] = 0.1
        w[[13,14,15,16]] = 0.2
        w[[21]] = 0.1
        w[[24]] = 0.4
        w[[26,27]] = 0.1

    return w
