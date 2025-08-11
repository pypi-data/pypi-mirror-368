import numpy as np
from scipy.interpolate import interp1d

class WavetableGenerator:

    def __init__(self, samples=2048, blend_values=512):
        self.samples = samples
        self.blend_values = blend_values

    def gen_wavetable(self, preset = "default", waves=None):
        
        if waves is None:
            waves = self.preset(preset)
        
        keys = np.array(waves)

        positions = np.linspace(0, 1, len(keys))

        interp = interp1d(positions, keys, axis=0)

        blend_positions = np.linspace(0, 1, self.blend_values)
        wavetable = interp(blend_positions)

        for i, wave in enumerate(waves):
            exact_position = int(i * (self.blend_values - 1) / (len(waves) - 1))
            wavetable[exact_position, :] = wave

        return wavetable
    
    def sine(self):
        return np.sin(np.linspace(0, 2 * np.pi, self.samples, endpoint=False))
    
    def triangular(self):
        rising = np.linspace(-1, 1, int(self.samples / 2), endpoint=False)
        falling = np.linspace(1, -1, int(self.samples / 2), endpoint=False)
        wave = np.concatenate((rising, falling))
        
        phase_shift = int(-self.samples / 4)
        return np.roll(wave, phase_shift)
    
    def square(self):
        return np.sign(self.sine())
    
    def sawtooth(self):
        return np.linspace(1, -1, self.samples, endpoint=False)
    
    def preset(self, preset):
        presets = {
            'default': [self.sine(), self.sawtooth()],
            'basic': [self.sine(), self.triangular(), self.square(), self.sawtooth()],
            'smooth': [self.sine(), self.triangular()],
            'harsh': [self.square(), self.sawtooth()]
        }

        if preset not in presets:
            raise ValueError(f"Preset '{preset}' not found. Available presets: {list(presets.keys())}")

        return presets[preset]
    
