from typing import Union

from copy import deepcopy

import numpy as np

from sound_arcanum.base.signal import AudioSignal, DEFAULT_SAMPRATE
from sound_arcanum.effects.effect import SignalEffect


class HardClip(SignalEffect):
    name = "Hard-clip Distortion"
    plugin_id = "hard-clip"
    arg_list = ["threshold"]

    def __init__(
        self,
        signal: AudioSignal = None,
        threshold: float = 0.5
    ):
        self.threshold = threshold
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()

        data = np.clip(data, -self.threshold, self.threshold)
        return self._as_signal(data)
    

class SoftClip(SignalEffect):
    name = "Soft-clip Distortion"
    plugin_id = "soft-clip"
    arg_list = ["drive"]

    def __init__(
        self,
        signal: AudioSignal = None,
        drive: float = 3.0
    ):
        self.drive = drive
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        data = np.tanh(data * self.drive)
        return self._as_signal(data)
    

class BitCrush(SignalEffect):
    name = "Bitcrushing"
    plugin_id = "bit-crush"
    arg_list = ["bits"]

    def __init__(
        self,
        signal: AudioSignal = None,
        bits: int = 4
    ):
        self.bits = bits
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()

        levels = 2 ** self.bits
        data = np.round(data * levels) / levels
        return self._as_signal(data)
    

class DownSample(SignalEffect):
    name = "Downsampling"
    plugin_id = "down-sample"
    arg_list = ["factor"]

    def __init__(
        self,
        signal: AudioSignal = None,
        factor: int = 4
    ):
        self.factor = factor
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        data = np.repeat(data[::self.factor], self.factor)
        return self._as_signal(data)
    

class CombFilter(SignalEffect):
    name = "Phase-like Comb-filter"
    plugin_id = "comb-filter"
    arg_list = [
        "delay_samples",
        "feedback",
    ]

    def __init__(
        self,
        signal: AudioSignal = None,
        delay_samples: int = 200,
        feedback: float = 0.5
    ):
        self.delay_samples = delay_samples
        self.feedback = feedback
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        for i in range(self.delay_samples, len(data)):
            data[i] += self.feedback * data[i - self.delay_samples]

        return self._as_signal(data)
    

class Tremolo(SignalEffect):
    name = "Tremolo"
    plugin_id = "tremolo"
    arg_list = [
        "osc_rate",
        "depth",
    ]

    def __init__(
        self,
        signal: AudioSignal = None,
        osc_rate: float = 5.0,
        depth: float = 0.5
    ):
        self.osc_rate = osc_rate
        self.depth = depth
        self.sample_rate = getattr(signal, "sample_rate", DEFAULT_SAMPRATE)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        t = np.linspace(0, len(data) / self.sample_rate, len(data), endpoint=False)

        lfo = 1 - self.depth + self.depth * np.sin(2 * np.pi * self.osc_rate * t)

        data = data * lfo

        return self._as_signal(data)
    

class ReverseAudio(SignalEffect):
    name = "Reverse Audio"
    plugin_id = "reverse-audio"
    arg_list = []

    def __init__(self, signal: AudioSignal = None):
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        data = data[::-1]

        return self._as_signal(data)
    

class LowPassFilter(SignalEffect):
    name = "Low-pass Filter"
    plugin_id = "low-pass-filter"
    arg_list = ["window_size"]

    def __init__(
        self,
        signal: AudioSignal = None,
        window_size: int = 100
    ):
        self.window_size = window_size
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        data = np.convolve(
            data,
            np.ones(self.window_size)/self.window_size,
            mode="same"
        )
        return self._as_signal(data)
    

class CheapDelay(SignalEffect):
    name = "Cheap Delay Effect"
    plugin_id = "cheap-delay"
    arg_list = [
        "delay_time",
        "feedback",
    ]

    def __init__(
        self,
        signal: AudioSignal = None,
        delay_time: float = 0.5,
        feedback: float = 0.5
    ):
        self.delay_time = delay_time
        self.feedback = feedback
        self.sample_rate = getattr(signal, "sample_rate", DEFAULT_SAMPRATE)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()

        delay_samples = int(self.delay_time * self.sample_rate)
        new = np.zeros_like(data)

        for i in range(delay_samples, len(data)):
            new[i] = data[i] + self.feedback * data[i - delay_samples]
        
        return self._as_signal(new)
    

class AddWhiteNoise(SignalEffect):
    name = "Add White-noise"
    plugin_id = "white-noise"
    arg_list = ["noise_level"]

    def __init__(
        self,
        signal: AudioSignal = None,
        noise_level: float = 0.02
    ):
        self.noise_level = noise_level
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()

        noise = np.random.normal(0, self.noise_level, size=data.shape)
        data = data * noise

        return self._as_signal(data)
    

class LowFreqOscillator(SignalEffect):
    name = "Low-frequency Oscillator"
    plugin_id = "lfo"
    arg_list = ["modulate_freq"]

    def __init__(
        self,
        signal: AudioSignal = None,
        modulate_freq: float = 5.0
    ):
        self.modulate_freq = modulate_freq
        self.sample_rate = getattr(signal, "sample_rate", DEFAULT_SAMPRATE)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        t = np.linspace(0, len(data) / self.sample_rate, len(data), endpoint=False)

        lfo = 0.5 * (1 * np.sin(2 * np.pi * self.modulate_freq * t))

        data = data * lfo
        return self._as_signal(data)
    

class RingModulator(SignalEffect):
    name = "Ring Modulator"
    plugin_id = "ring-modulator"
    arg_list = ["modulator_wave"]

    def __init__(
        self,
        signal: AudioSignal = None,
        modulator_wave: Union[AudioSignal, np.ndarray] = None
    ):
        if isinstance(modulator_wave, AudioSignal):
            self.modulator_wave = modulator_wave.safe_buffer()
        elif isinstance(modulator_wave, np.ndarray):
            self.modulator_wave = deepcopy(modulator_wave)

        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        data = data * self.modulator_wave

        return self._as_signal(data)
    

class VolumeEnvelope(SignalEffect):
    name = "Volume Envelope"
    plugin_id = "volume-envelope"
    arg_list = ["fade_duration"]

    def __init__(
        self,
        signal: AudioSignal = None,
        fade_duration: float = 0.5
    ):
        self.fade_duration = fade_duration
        self.sample_rate = getattr(signal, "sample_rate", DEFAULT_SAMPRATE)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()

        length = len(data)
        fade_in = np.linspace(0, 1, int(self.sample_rate * self.fade_duration))
        sustain = np.ones(length - 2 * len(fade_in))
        fade_out = np.linspace(1, 0, len(fade_in))

        envelope = np.concatenate((fade_in, sustain, fade_out))
        data = data[:len(envelope)] * envelope

        return self._as_signal(data)
    

class HighPassFilter(SignalEffect):
    name = "High-pass Filter"
    plugin_id = "high-pass-filter"
    arg_list = ["window_size"]

    def __init__(
        self,
        signal: AudioSignal = None,
        window_size: int = 100
    ):
        self.window_size = window_size
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()

        low_passed = np.convolve(data, np.ones(self.window_size) / self.window_size, mode="same")
        data = data - low_passed

        return self. _as_signal(data)
    

class PhaserEffect(SignalEffect):
    name = "Phaser Effect"
    plugin_id = "phaser"
    arg_list = ["depth", "rate"]

    def __init__(
        self,
        signal: AudioSignal = None,
        depth: float = 0.7,
        rate: float = 0.25
    ):
        self.depth = depth
        self.rate = rate
        self.sample_rate = getattr(signal, "sample_rate", DEFAULT_SAMPRATE)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        t = np.linspace(0, len(data) / self.sample_rate, len(data), endpoint=False)

        lfo = self.depth * np.sin(2 * np.pi * self.rate * t)

        output = np.zeros_like(data)
        for i in range(1, len(data)):
            output[i] = data[i] + lfo[i] * data[i - 1]

        return self. _as_signal(output)
    

class AutoWah(SignalEffect):
    name = "Auto-wah Filter"
    plugin_id = "auto-wah"
    arg_list = [
        "base_freq",
        "depth",
        "rate",
    ]

    def __init__(
        self,
        signal: AudioSignal = None,
        base_freq: float = 500.0,
        depth: float = 300.0,
        rate: float = 1.0
    ):
        self.base_freq = base_freq
        self.depth = depth
        self.rate = rate
        self.sample_rate = getattr(signal, "sample_rate", DEFAULT_SAMPRATE)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        from scipy.signal import butter, lfilter

        def bandpass(data, lowcut, highcut, fs, order=2):
            nyq = 0.5 * fs
            low = lowcut / nyq
            high = highcut / nyq
            b, a = butter(order, [low, high], btype="band")
            return lfilter(b, a, data)
        
        sig = self.input_signal.safe_buffer()
        t = np.arange(len(sig)) / self.sample_rate
        center_freq = self.base_freq + self.depth * np.sin(2 * np.pi * self.rate * t)

        out = np.zeros_like(sig)
        for i in range(0, len(sig), 512):
            f = center_freq[i]
            chunk = sig[i : i + 512]
            out[i : i + 512] = bandpass(
                chunk,
                f * 0.8,
                f * 1.2,
                self.sample_rate
            )
        
        return self. _as_signal(out)
    

class ChorusEffect(SignalEffect):
    name = "Chorus Effect"
    plugin_id = "chorus"
    arg_list = [
        "depth",
        "rate",
        "mix",
    ]

    def __init__(
        self,
        signal: AudioSignal = None,
        depth: float = 0.002,
        rate: float = 0.25,
        mix: float = 0.5
    ):
        self.depth = depth
        self.rate = rate
        self.mix = mix
        self.sample_rate = getattr(signal, "sample_rate", DEFAULT_SAMPRATE)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        t = np.arange(len(data)) / self.sample_rate

        mod = self.depth * self.sample_rate * np.sin(2 * np.pi * self.rate * t)
        mod = mod.astype(int)

        out = np.zeros_like(data)

        for i in range(len(data)):
            delay_i = i - mod[i] if i - mod[i] >= 0 else 0
            out[i] = data[i] + self.mix * data[delay_i]

        out /= np.max(np.abs(out))
        return self._as_signal(out)
    

class Vibrato(SignalEffect):
    name = "Vibrato"
    plugin_id = "vibrato"
    arg_list = ["depth", "rate"]

    def __init__(
        self,
        signal: AudioSignal = None,
        depth: float = 0.002,
        rate: float = 5.0
    ):
        self.depth = depth
        self.rate = rate
        self.sample_rate = getattr(signal, "sample_rate", DEFAULT_SAMPRATE)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        t = np.arange(len(data))

        mod = self.depth * self.sample_rate * np.sin(2 * np.pi * self.rate * t / self.sample_rate)
        indices = (t + mod).astype(int)
        indices = np.clip(indices, 0, len(data) - 1)
        return self._as_signal(data[indices])
    

class GainBoost(SignalEffect):
    name = "Gain Booster"
    plugin_id = "gain-boost"
    arg_list = ["gain"]

    def __init__(
        self,
        signal: AudioSignal = None,
        gain: float = 1.0
    ):
        self.gain = gain
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        data = data * self.gain
        data = np.clip(data, -1.0, 1.0)
        return self._as_signal(data)
    

class FadeOut(SignalEffect):
    name = "Fade Out Ending"
    plugin_id = "fade-out"
    arg_list = ["duration"]

    def __init__(
        self,
        signal: AudioSignal = None,
        duration: float = 1.0
    ):
        self.duration = duration
        self.sample_rate = getattr(signal, "sample_rate", DEFAULT_SAMPRATE)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        fade_samples = int(self.sample_rate * self.duration)
        fade_curve = np.linspace(1, 0, fade_samples)
        data[-fade_samples:] *= fade_curve

        return self._as_signal(data)
    


        