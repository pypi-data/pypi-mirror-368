import numpy as np
from scipy.signal import butter, filtfilt
from .MiniSynth import MiniSynth
from .Scale import Scale

class MiniSynthFM(MiniSynth):
    def __init__(self, wavetable, sr=44100, duration=10.0):
        self.sr = sr
        self.duration = duration
        self.samples = int(sr * duration)
        
        if wavetable is None:
            raise ValueError("Wavetable must be provided.")
        self.wavetable = wavetable

        self.set_base_freq(np.array([440.0]))
        self.set_amp(np.array([1.0]))

        self.set_mod_freq_ratio(np.array([1.0]))
        self.set_mod_shape(np.array([0.0]))
        
        self.set_carr_shape(np.array([0.0]))
        self.set_fm_amount(np.array([0.0]))
    
    def get_base_freq(self):
        return self._base_freq

    def set_base_freq(self, freq:np.ndarray):
        self._base_freq = self._stretch_array(freq, self.samples)

    def get_amp(self):
        return self._amp

    def set_amp(self, amp:np.ndarray):
        self._amp = self._stretch_array(amp, self.samples)

    def get_mod_freq_ratio(self):
        return self._mod_freq_ratio

    def set_mod_freq_ratio(self, ratio:np.ndarray):
        self._mod_freq_ratio = self._stretch_array(ratio, self.samples)

    def get_mod_shape(self):   
        return self._mod_shape

    def set_mod_shape(self, shape:np.ndarray):
        self._mod_shape = self._stretch_array(shape, self.samples)

    def get_carr_shape(self):
        return self._carr_shape

    def set_carr_shape(self, shape:np.ndarray):
        self._carr_shape = self._stretch_array(shape, self.samples)

    def get_fm_amount(self):
        return self._fm_amount

    def set_fm_amount(self, amount:np.ndarray):
        self._fm_amount = self._stretch_array(amount, self.samples)

    def get_parameters(self):
        return {
            "base_freq": {
                "get": self.get_base_freq,
                "set": self.set_base_freq,
                "range": (20.0, 5000.0),
                "scale": Scale.LOGARITHMIC
            },
            "amp": {
                "get": self.get_amp,
                "set": self.set_amp,
                "range": (0.0, 1.0),
                "scale": Scale.LINEAR
            },
            "mod_freq_ratio": {
                "get": self.get_mod_freq_ratio,
                "set": self.set_mod_freq_ratio,
                "range": (0.01, 10.0),
                "scale": Scale.LOGARITHMIC
            },
            "mod_shape": {
                "get": self.get_mod_shape,
                "set": self.set_mod_shape,
                "range": (0.0, 1.0),
                "scale": Scale.LINEAR
            },
            "carr_shape": {
                "get": self.get_carr_shape,
                "set": self.set_carr_shape,
                "range": (0.0, 1.0),
                "scale": Scale.LINEAR
            },
            "fm_amount": {
                "get": self.get_fm_amount,
                "set": self.set_fm_amount,
                "range": (0.0, 1.0),
                "scale": Scale.LINEAR
            }
        }


    def render(self):
        mod_audio = self._wavetable_osc(
            frequency=self._base_freq * self._mod_freq_ratio,
            shape=self._mod_shape,
            wavetable=self.wavetable
        )

        frequency = mod_audio * self._fm_amount * self._base_freq + self._base_freq

        carr_audio = self._wavetable_osc(
            frequency=frequency,
            shape=self._carr_shape,
            wavetable=self.wavetable
        )
        audio =  self._amp * carr_audio
        audio = self._apply_antialiasing(audio)
        
        return audio
    
    # def _wavetable_osc(self, frequency, shape, wavetable):
        
    #     phase = np.cumsum(frequency) / self.sr
        
    #     wave_indices_float = shape * (wavetable.shape[0] - 1)
    #     wave_idx1 = np.clip(wave_indices_float.astype(int), 0, wavetable.shape[0] - 1)
    #     wave_idx2 = np.clip(wave_idx1 + 1, 0, wavetable.shape[0] - 1)
    #     wave_blend = wave_indices_float - wave_idx1
        
    #     table_positions = ((phase % 1.0) * wavetable.shape[1]).astype(int) % wavetable.shape[1]
        
    #     sample1 = wavetable[wave_idx1, table_positions]
    #     sample2 = wavetable[wave_idx2, table_positions]
    #     output = sample1 * (1 - wave_blend) + sample2 * wave_blend
        
    #     return output
    
    def __str__(self):
        return (f"MiniSynth(sampling_rate={self.sr}, duration={self.duration}, "
                f"base_freq={self._base_freq}, amp={self._amp}, "
                f"mod_freq_ratio={self._mod_freq_ratio}, mod_shape={self._mod_shape}, "
                f"carr_shape={self._carr_shape}, fm_amount={self._fm_amount})")
    
    def _stretch_array(self, arr:np.ndarray, target_length:int):
        old_indices = np.arange(len(arr))
        new_indices = np.linspace(0, len(arr) - 1, target_length)
        
        return np.interp(new_indices, old_indices, arr)
    
    def _apply_antialiasing(self, audio):
        
        cutoff = self.sr / 2.2
        nyquist = self.sr / 2
        normalized_cutoff = cutoff / nyquist
        
        b, a = butter(4, normalized_cutoff, btype='low')
        audio = filtfilt(b, a, audio)
        
        return audio