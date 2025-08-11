import numpy as np
from scipy.signal import butter, filtfilt

from .Scale import Scale
from .MiniSynth import MiniSynth

class MiniSynthSubtractive(MiniSynth):
    def __init__(self, sr=44100, duration=10.0):
        self.sr = sr
        self.duration = duration
        self.samples = int(sr * duration)

        self.set_base_freq(np.array([440.0]))
        self.set_amp(np.array([1.0]))

        self.set_filter_cutoff(np.array([10000.0]))
        self.set_osc_shape(np.array([0.0]))

    def get_base_freq(self):
        return self._base_freq

    def set_base_freq(self, freq:np.ndarray):
        self._base_freq = self._lowpass(self._stretch_array(freq, self.samples))

    def get_amp(self):
        return self._amp

    def set_amp(self, amp:np.ndarray):
        self._amp = self._lowpass(self._stretch_array(amp, self.samples))

    def get_filter_cutoff(self):
        return self._filter_cutoff

    def set_filter_cutoff(self, cutoff:np.ndarray):
        self._filter_cutoff = self._lowpass(self._stretch_array(cutoff, self.samples))

    def get_osc_shape(self):
        return self._osc_shape

    def set_osc_shape(self, shape:np.ndarray):
        self._osc_shape = self._lowpass(self._stretch_array(shape, self.samples))

    def get_parameters(self):
        return {
            "base_freq": {
                "get": self.get_base_freq,
                "set": self.set_base_freq,
                "range": (50.0, 1000.0),
                "scale": Scale.LOGARITHMIC
            },
            "amp": {
                "get": self.get_amp,
                "set": self.set_amp,
                "range": (0.0, 1.0),
                "scale": Scale.LOGARITHMIC
            },
            "filter_cutoff": {
                "get": self.get_filter_cutoff,
                "set": self.set_filter_cutoff,
                "range": (200.0, 5000.0),
                "scale": Scale.LOGARITHMIC
            },
            "osc_shape": {
                "get": self.get_osc_shape,
                "set": self.set_osc_shape,
                "range": (0.0, 1.0),
                "scale": Scale.LINEAR
            }
        }
    
    def render(self):
        if not hasattr(self, '_base_freq') or not hasattr(self, '_amp'):
            raise ValueError("Base frequency and amplitude must be set before rendering.")

        audio = self._square_saw_osc(frequency=self.get_base_freq(), blend=self.get_osc_shape())  
        audio *= self._amp

        audio = self._filter_audio(audio)
        audio = self._apply_antialiasing(audio)

        return audio

    def _filter_audio(self, audio):
        output = np.zeros_like(audio)
        y1 = 0.0  # First filter state
        y2 = 0.0  # Second filter state

        for i in range(len(audio)):
            cutoff = self._filter_cutoff[i]
            x = 2 * np.pi * cutoff / self.sr
            alpha = x / (x + 1)
            
            y1 = y1 + alpha * (audio[i] - y1)
            
            y2 = y2 + alpha * (y1 - y2)
            
            output[i] = y2

        return output