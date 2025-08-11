import numpy as np
from enum import Enum
from .Scale import Scale
from scipy.signal import butter, filtfilt

class Mod(Enum):
    TIME = 0
    AMPLITUDE = 1
    CONVEXITY = 2

class ModGenerator:

    def __init__(self, sr=44100, duration=10.0):
        self.sr = sr
        self.duration = duration
        self.samples = int(sr * duration)

    def render(self):
        env =np.zeros(self.samples)

        for i in range(1, self.points.shape[1]):
            start_index = int(self.points[Mod.TIME.value, i-1])
            end_index = int(self.points[Mod.TIME.value, i])

            start_amplitude = self.points[Mod.AMPLITUDE.value, i-1]
            end_amplitude = self.points[Mod.AMPLITUDE.value, i]

            segment = np.linspace(0, 1, end_index - start_index)
            segment = segment ** self.points[Mod.CONVEXITY.value,i-1] 
            segment *= (end_amplitude - start_amplitude)
            segment += start_amplitude

            env[start_index:end_index] = segment

        env = self._lowpass(env, cutoff=20.0, order=4)
        return env


    def init_points_random(self, num_points=16, min:float= 0.0, max:float=1.0, convexity=3.0, scale:Scale=Scale.LINEAR):

        if num_points < 2:
            raise ValueError("At least two points are required")
        
        self.points = np.random.rand(3, num_points)

        self.points[Mod.TIME.value,:] = np.sort(self.points[Mod.TIME.value,:])

        self.points[Mod.TIME.value,:] = np.round(self.points[Mod.TIME.value,:]*self.samples)
        self.points[Mod.TIME.value,0] = 0
        self.points[Mod.TIME.value,-1] = self.samples

        if scale == Scale.LOGARITHMIC:
            if min == 0:
                self.points[Mod.AMPLITUDE.value,:] = max * (self.points[Mod.AMPLITUDE.value,:] ** 2)
            else:
                self.points[Mod.AMPLITUDE.value,:] = min * (max / min) ** self.points[Mod.AMPLITUDE.value,:]
        elif scale == Scale.LINEAR:
            self.points[Mod.AMPLITUDE.value,:] = min + (max - min) * self.points[Mod.AMPLITUDE.value,:]

        self.points[Mod.CONVEXITY.value,:]*= convexity

        return self
    
    def get_points(self):
        if not hasattr(self, 'points'):
            raise ValueError("Points have not been initialized. Use init_points_random or set_points.")
        
        return self.points

    def set_points(self, points):
        if points.shape[0] != 3:
            raise ValueError("Points must have shape (3, num_points)")
        if points.shape[1] < 2:
            raise ValueError("At least two points are required")
        
        self.points = points
        self.points[Mod.TIME.value,:] = np.sort(self.points[Mod.TIME.value,:])
        
        if self.points[Mod.TIME.value,0] != 0:
            self.points[Mod.TIME.value,0] = 0
        if self.points[Mod.TIME.value,-1] != self.samples:
            self.points[Mod.TIME.value,-1] = self.samples
        
        return self
    
    def get_plot_points(self):
        return self.points[Mod.TIME.value,:], self.points[Mod.AMPLITUDE.value,:]
    
    def _lowpass(self, data, cutoff=20.0, order=4):
        b, a = butter(order, cutoff / (0.5 * self.sr), btype='low')
        return filtfilt(b, a, data)
    
