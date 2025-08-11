### MiniSynth
A Python-based modular synthesizer framework for generating audio and datasets with controllable parameters.

## Overview
MiniSynth provides a flexible framework for creating different types of synthesizers with time-varying parameters. The project includes:

# Components
- Subtractive synthesis (MiniSynthSubtractive) - Traditional synthesis with oscillators and filters
- FM synthesis (MiniSynthFM) - Frequency modulation synthesis using wavetables
- Wavetable generation (WavetableGenerator) - Create custom waveforms and wavetables
- Parameter modulation (ModGenerator) - Generate time-varying control signals
- Dataset management (DatasetManager) - Generate and manage synthesis datasets


# Features
- Multiple synthesis methods (subtractive, FM)
- Wavetable synthesis with interpolation
- Time-varying parameter modulation with customizable envelopes
- Built-in waveforms: sine, triangle, square, sawtooth
- Anti-aliasing filters
- Dataset generation for machine learning applications
- Linear and logarithmic parameter scaling