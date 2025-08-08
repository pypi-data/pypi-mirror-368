from copy import deepcopy

from typing import Tuple, Iterable, List

import numpy as np

from sound_arcanum.base.signal import AudioSignal, DEFAULT_SAMPRATE
from sound_arcanum.generators.generator import SignalGenerator


class AmbientPad(SignalGenerator):
    name = "Ambient Synth-pad"
    plugin_id = "ambient-pad"
    arg_list = [
        "frequency",
        "duration",
        "sample_rate",
    ]

    def __init__(
        self,
        frequency: float = 220.0,
        duration: float = 3.0,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.frequency = frequency
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        t = np.linspace(0, self.duration, int(self.duration * self.sample_rate))

        osc_a = np.sin(2 * np.pi * self.frequency * t)
        osc_b = np.sin(2 * np.pi * (self.frequency * 1.01) * t)
        osc_c = np.sin(2 * np.pi * (self.frequency * 0.99) * t)

        vibrato = np.sin(2 * np.pi * 5 * t) * 0.01
        osc_vibrato = np.sin(2 * np.pi * (self.frequency * vibrato) * t)

        envelope = np.clip(t / 1.5, 0, 1) * np.exp(-t / 4)
        pad = (osc_a + osc_b + osc_c + osc_vibrato) * 0.25 * envelope

        pad /= np.max(np.abs(pad))

        return self._as_signal(pad)
    

class PluckSynth(SignalGenerator):
    name = "Pluck Synth"
    plugin_id = "pluck-synth"
    arg_list = [
        "frequency",
        "duration", 
        "sample_rate",
    ]

    def __init__(
        self,
        frequency: float = 440.0,
        duration: float = 0.5,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.frequency = frequency
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        t = np.linspace(0, self.duration, int(self.duration * self.sample_rate))

        saw_wave = 2 * (t * self.frequency % 1) - 1
        envelope = np.exp(-t * 10)

        data = saw_wave * envelope
        return self._as_signal(data)
    

class CyberBass(SignalGenerator):
    name = "Cyberpunk Bass"
    plugin_id = "cyber-bass"
    arg_list = [
        "frequency",
        "duration",
        "sample_rate",
    ]

    def __init__(
        self,
        frequency: float = 100.0,
        duration: float = 1.0,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.frequency = frequency
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        t = np.linspace(0, self.duration, int(self.duration * self.sample_rate))

        arp = self.frequency * (1 + 0.2 * np.sin(2 * np.pi * 4 * t))
        phase = np.cumsum(arp) / self.sample_rate
        square_wave = np.sign(np.sin(2 * np.pi * phase))

        envelope = np.exp(-t * 2)
        data = np.tanh(square_wave * 5) * envelope

        return self._as_signal(data)
    


class ModulatedSine(SignalGenerator):
    name = "Modulated Sine-wave"
    plugin_id = "modulated-sine"
    arg_list = [
        "frequency",
        "modulation_freq",
        "factor",
        "duration",
        "sample_rate",
    ]

    def __init__(
        self,
        frequency: float = 440.0,
        modulation_freq: float = 439.0,
        factor: float = 2.0,
        duration: float = 6.0,
        amplitude: float = 1.0,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.frequency = frequency
        self.modulation_freq = modulation_freq
        self.factor = factor
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        t = np.linspace(0, self.duration * 2 * np.pi, int(self.duration * self.sample_rate))

        data = np.sin(self.frequency * t + (np.sin(self.modulation_freq * t) * self.factor))

        data *= self.amplitude
        return self._as_signal(data)
    

# class PhaseModulatedSine(SignalGenerator):
#     name = "Phased Frequency-modulated Sine-wave"
#     plugin_id = "phased-modulated-sine"
#     arg_list = [
#         "frequency",
#         "modulation_freq",
#         "duration",
#         "amplitude",
#         "sample_rate",
#     ]

#     def __init__(
#         self,
#         frequency: float = 880.0,
#         modulation_freq: float = 73.3333,
#         duration: float = 6.0,
#         amplitude: float = 1.0,
#         sample_rate: int = DEFAULT_SAMPRATE
#     ):
#         self.frequency = frequency
#         self.modulation_freq = modulation_freq
#         self.duration = duration
#         self.amplitude = amplitude
#         self.sample_rate = sample_rate

#     def _process(self) -> AudioSignal:
#         t = np.linspace(0, self.duration * 2 * np.pi, int(self.duration * self.sample_rate))
#         ramp = np.logspace(0, 1, int(self.duration * self.sample_rate))

#         data = np.sin(self.frequency * t + ramp * np.sin(self.modulation_freq * t))
#         data *= self.amplitude

#         return self._as_signal(data)
    


class RampModulation(SignalGenerator):
    name = "Ramped Freuency Modulated Sine"
    plugin_id = "ramp-modulation-sine"
    arg_list = [
        "frequency",
        "modulation_freq",
        "ramp_amount",
        "duration",
        "amplitude",
        "sample_rate",
    ]

    def __init__(
        self,
        frequency: float = 440.0,
        modulation_freq: float = 80.0,
        ramp_amount: float = 0.6,
        duration: float = 2.0,
        amplitude: float = 1.0,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.frequency = frequency
        self.modulation_freq = modulation_freq
        self.ramp_amount = ramp_amount
        self.duration = duration
        self.amplitude = amplitude
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        ramp = np.logspace(0, 1, int(self.duration * self.sample_rate)) * self.ramp_amount
        t = np.linspace(0, self.duration * 2 * np.pi, int(self.duration * self.sample_rate))

        data = np.sin(self.frequency * t + ramp * np.sin(self.modulation_freq * t))

        data *= self.amplitude

        return self._as_signal(data)
    

def sine_mod(plugin, tspace: np.ndarray) -> np.ndarray:
    freq = getattr(plugin, "modulation_freq", 0.0)
    # duration = getattr(plugin, "duration", 1.0)
    # sample_rate = getattr(plugin, "sample_rate", DEFAULT_SAMPRATE)
    return np.sin(freq * tspace)


def sine(frequency: float, tspace: np.ndarray) -> np.ndarray:
    return np.sin(frequency * tspace) * 0.3


def triangle_sig1(plugin, tspace: np.ndarray) -> np.ndarray:
    freqs = getattr(plugin, "modulation_freqs", (0.0, 0.0))
    r_amount = getattr(plugin, "ramp_amount", 2)

    freq_a, freq_b = freqs
    ramp = np.logspace(1, 0, int(plugin.duration * plugin.sample_rate)) * r_amount

    data = 2 / np.pi * np.arcsin(np.sin(freq_a * tspace + ramp * sine(freq_b, tspace))) * 0.3
    return data


def triangle_sig2(plugin, tspace: np.ndarray) -> np.ndarray:
    frequency = plugin.frequency
    return 2 / np.pi * np.arcsin(np.sin(frequency * tspace)) * 0.3


def triangle_mod(plugin, tspace: np.ndarray) -> np.ndarray:
    frequency = plugin.frequency
    ramp_amount = plugin.ramp_amount
    mod_freq = plugin.modulation_freq

    ramp = np.logspace(0, 1, int(plugin.duration * plugin.sample_rate)) * ramp_amount

    data = 2 / np.pi * np.arcsin(np.sin(frequency * tspace + ramp * np.sin(mod_freq * tspace))) * 0.3

    return data


def lfo(plugin, tspace: np.ndarray) -> np.ndarray:
    lfo_freq = plugin.lfo_frequency
    lfo_amt = plugin.lfo_amount
    y = np.sin(lfo_freq * tspace)

    y = (y * lfo_amt / 2 + (1 - lfo_amt / 2))
    return y


class PhaseChord(SignalGenerator):
    name = "Phased Triangle Chord"
    plugin_id = "phase-chord"
    arg_list = [
        "modulators",
        "notes_pair_a",
        "notes_pair_b",
        "notes_pair_c",
        "lfo_frequency",
        "lfo_amount",
        "ramp_amount",
        "duration",
        "sample_rate"
    ]

    def __init__(
        self,
        modulators: Tuple[float] = (400.0, 300.0),
        notes_pair_a: Tuple[float] = (55.0, 440.0),
        notes_pair_b: Tuple[float] = (932.3275, 1864.655,),
        notes_pair_c: Tuple[float] = (622.2540, 82.40689,),
        lfo_frequency: float = 10.0,
        lfo_amount: float = 0.1,
        ramp_amount: int = 5,
        duration: float = 6.0,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.modulators = modulators
        self.notes = [
            notes_pair_a,
            notes_pair_b,
            notes_pair_c
        ]
        self.lfo_frequency = lfo_frequency
        self.lfo_amount = lfo_amount
        self.ramp_amount = ramp_amount
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        mod1, mod2 = self.modulators
        first = self.notes[0]
        mid = self.notes[1]
        last = self.notes[2]
        high_mid = max(mid)
        high_last = max(last)
        low_mid = min(mid)
        low_last = min(last)
        low_first = min(first)

        t = np.linspace(0, self.duration * 2 * np.pi, int(self.duration * self.sample_rate))
        ramp_a = np.logspace(0, 1, int(self.duration * self.sample_rate)) * self.ramp_amount
        ramp_b = np.logspace(1, 0, int(self.duration * self.sample_rate)) * self.ramp_amount

        def sine(freq):
            return np.sin(freq * t) * 0.3
        
        def triangle(freq1, freq2):
            y = 2 / np.pi * np.arcsin(np.sin(freq1 * t + ramp_b * sine(freq2))) * 0.3
            return y
        
        def triangle2(freq):
            y = 2 / np.pi * np.arcsin(np.sin(freq * t)) * 0.3
            return y
        
        def triangle_mod(freq1, freq2):
            # y = 2 / np.pi * np.arcsin(np.sin())
            y = 2 / np.pi * np.arcsin(np.sin(freq1 * t + ramp_a * np.sin(freq2 * t))) * 0.3
            return y
        
        def lfo(freq, amount):
            y = np.sin(freq * t)
            y = (y * amount / 2 + (1 - amount / 2))
            return y
        
        data = ((triangle_mod(mod1) + sine(mod2) + triangle(high_mid, high_last)
                 + triangle2(low_mid) + sine(low_last) + sine(low_first)) * lfo(self.lfo_frequency, self.lfo_amount)) * 0.3
        
        return self._as_signal(data)
    
