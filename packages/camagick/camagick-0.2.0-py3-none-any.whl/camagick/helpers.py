#!/usr/bin/python3

from numpy import zeros, sqrt
import math, time

class FpsCounter:
    def __init__(self, pts=100, label="FPS"):
        self.told = time.time()
        self.told_diff = 0
        self.fps_history = zeros(pts)
        self.ji = 0
        self.label = label
        
    def mark(self):
        tnow = time.time()
        tdiff = 1/(tnow-self.told)
        self.fps_history[self.ji] = tdiff
        self.ji = (self.ji+1)%self.fps_history.shape[0]
        self.told = tnow

    @property
    def fps(self):
        return self.fps_history.mean()

    @property
    def jitter(self):
        return sqrt( ((self.fps_history-self.fps_history.mean())**2).mean() )

    def __str__(self):
        return "%s: %2.1f ± %d Hz" % (self.label, self.fps, math.ceil(self.jitter))


    def __repr__(self):
        return str(self)
