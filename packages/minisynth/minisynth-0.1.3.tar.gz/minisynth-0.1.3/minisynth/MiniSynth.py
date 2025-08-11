from abc import ABC, abstractmethod
import numpy as np
from scipy.signal import butter, filtfilt

class MiniSynth(ABC):

    @abstractmethod
    def render(self):
        """Render the audio output of the synthesizer."""
        pass

    @abstractmethod
    def get_parameters(self):
        """
        Return a dictionary of methods and ranges for the synthesizer parameters.
        The keys should be the parameter names and the values getters, setters, and ranges.
        Example:
        {
            "base_freq": {
                "get": self.get_base_freq,
                "set": self.set_base_freq,
                "range": (20.0, 20000.0),
                "scale": Scale.LOGARITHMIC
            },
            "amp": {
                "get": self.get_amp,
                "set": self.set_amp,
                "range": (0.0, 1.0),
                "scale": Scale.LINEAR
            }
        }
        """
        pass

    def _wavetable_osc(self, frequency, shape, wavetable):
        
        phase = np.cumsum(frequency) / self.sr
        
        wave_indices_float = shape * (wavetable.shape[0] - 1)
        wave_idx1 = np.clip(wave_indices_float.astype(int), 0, wavetable.shape[0] - 1)
        wave_idx2 = np.clip(wave_idx1 + 1, 0, wavetable.shape[0] - 1)
        wave_blend = wave_indices_float - wave_idx1
        
        table_positions = ((phase % 1.0) * wavetable.shape[1]).astype(int) % wavetable.shape[1]
        
        sample1 = wavetable[wave_idx1, table_positions]
        sample2 = wavetable[wave_idx2, table_positions]
        output = sample1 * (1 - wave_blend) + sample2 * wave_blend
        
        return output

    def _square_saw_osc(self, frequency:np.ndarray, blend:np.ndarray) -> np.ndarray:
        phase = np.cumsum(frequency) / self.sr % 1.0
        square_wave =  np.sign(np.sin(2 * np.pi * phase))
        saw_wave = (phase % 1.0) * 2 - 1

        return square_wave * (1 - blend) + saw_wave * blend
    

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
    
    def _lowpass(self, data, cutoff=20.0, order=4):
        b, a = butter(order, cutoff / (0.5 * self.sr), btype='low')
        return filtfilt(b, a, data)