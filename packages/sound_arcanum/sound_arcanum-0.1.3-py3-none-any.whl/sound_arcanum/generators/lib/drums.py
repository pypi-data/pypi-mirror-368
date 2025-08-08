from copy import deepcopy

import numpy as np

from sound_arcanum.base.signal import AudioSignal, DEFAULT_SAMPRATE
from sound_arcanum.generators.generator import SignalGenerator


class Tr808Kick(SignalGenerator):
    name = "TR-808 Kick"
    plugin_id = "tr808-kick"
    arg_list = [
        "bass_frequency",
        "duration",
        "pitch_decay",
        "sample_rate",
    ]

    def __init__(
        self,
        bass_frequency: float = 60.0,
        duration: float = 0.5,
        pitch_decay: float = 0.02,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.bass_frequency = bass_frequency
        self.duration = duration
        self.pitch_decay = pitch_decay
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        t = np.linspace(0, self.duration, int(self.duration * self.sample_rate))

        pitch_envelope = np.exp(-t / self.pitch_decay)
        sine_wave = np.sin(2 * np.pi * self.bass_frequency * pitch_envelope * t)

        envelope = np.exp(-t * 12)

        data = sine_wave * envelope

        return self._as_signal(data)
    

class Tr808Snare(SignalGenerator):
    name = "TR-808 Snare"
    plugin_id = "tr808-snare"
    arg_list = [
        "tone_frequency",
        "duration",
        "sample_rate",
    ]

    def __init__(
        self,
        tone_frequency: float = 180.0,
        duration: float = 0.5,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.tone_frequency = tone_frequency
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        t = np.linspace(0, self.duration, int(self.duration * self.sample_rate))

        noise = np.random.normal(0, 1, size=t.shape)
        envelope = np.exp(-t * 25)

        tone = np.sin(2 * np.pi * self.tone_frequency * t)
        tone_envelope = np.exp(-t * 20)

        data = 0.6 * noise * envelope + 0.4 * tone * tone_envelope

        return self._as_signal(data)
    

class Tr808HiHat(SignalGenerator):
    name = "TR-808 HiHat"
    plugin_id = "tr808-hihat"
    arg_list = [
        "envelope_factor",
        "duration",
        "sample_rate",
    ]

    def __init__(
        self,
        envelope_factor: int = 60,
        duration: float = 0.15,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.envelope_factor = envelope_factor
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        t = np.linspace(0, self.duration, int(self.duration * self.sample_rate))

        noise = np.random.normal(0, 1, size=t.shape)

        envelope = np.exp(-t * 60)
        hipass_filter = noise - np.roll(noise, 1)

        data = hipass_filter * envelope

        return self._as_signal(data)
    

class IndustrialKick(SignalGenerator):
    name = "Industrial Kick"
    plugin_id = "industrial-kick"
    arg_list = ["duration", "sample_rate"]

    def __init__(
        self,
        duration: float = 1.0,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        # from sound_arcanum.
        kick = Tr808Kick(duration=0.5, sample_rate=self.sample_rate).get_signal()
        kick = kick.safe_buffer()
        t = np.linspace(0, self.duration, int(self.duration * self.sample_rate))

        modulator = np.sin(2 * np.pi * 30 * t)
        carrier = np.sin(2 * np.pi * 90 * t + 5 * modulator)

        envelope = np.exp(-t * 2)
        bass = carrier * envelope

        distorted_bass = np.tanh(bass * 5)

        padded_kick = np.pad(kick, (0, len(distorted_bass) - len(kick)))
        combined = padded_kick + distorted_bass

        data = combined / np.max(np.abs(combined))

        return self._as_signal(data)
    

class IndustrialSnare(SignalGenerator):
    name = "Industrial Snare"
    plugin_id = "industrial-snare"
    arg_list = ["sample_rate"]

    def __init__(self, sample_rate: int = DEFAULT_SAMPRATE):
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        from sound_arcanum.generators.lib.waves import SineWave
        from sound_arcanum.effects.lib.common import CheapDelay

        snare = Tr808Snare(duration=0.4, sample_rate=self.sample_rate).get_signal()
        snare = snare.safe_buffer()

        modulator = SineWave(frequency=1200.0, duration=0.4, sample_rate=self.sample_rate).get_signal()
        modulator = modulator.safe_buffer()

        ringed = snare * modulator

        delayed = CheapDelay(
            signal=AudioSignal(ringed),
            delay_time=0.15,
            feedback=0.3,
            sample_rate=self.sample_rate
        ).get_signal()
        delayed = delayed.safe_buffer()

        final_wave = np.tanh(delayed * 3)

        data = final_wave / np.max(np.abs(final_wave))
        return self._as_signal(data)
    


class GlitchHiHat(SignalGenerator):
    name = "Glitch Hi-hat"
    plugin_id = "glitch-hihat"
    arg_list = ["sample_rate"]

    def __init__(
        self,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        duration = 1.0
        t = np.linspace(0, duration, int(duration * self.sample_rate))

        hihat = Tr808HiHat().get_signal().safe_buffer()
        pattern = np.zeros_like(t)

        for i in range(0, len(t), int(self.sample_rate * 0.25)):
            pattern[i : i + len(hihat)] += hihat

        bitcrushed = np.random.choice([-1, 0, 1], size=len(t)) * np.exp(-t * 4)

        data = pattern + 0.3 * bitcrushed
        data = data / np.max(np.abs(data))

        return self._as_signal(data)
    

class SubBassGlide(SignalGenerator):
    name = "Subsonic Bass Glide"
    plugin_id = "sub-bass-glide"
    arg_list = [
        "start_frequency",
        "end_frequency",
        "duration",
        "sample_rate",
    ]

    def __init__(
        self,
        start_frequency: float = 130.0,
        end_frequency: float = 50.0,
        duration: float = 1.5,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.start_frequency = start_frequency
        self.end_frequency = end_frequency
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        t = np.linspace(0, self.duration, int(self.duration * self.sample_rate))

        frequencies = np.logspace(np.log10(self.start_frequency), np.log10(self.end_frequency), len(t))
        phase = np.cumsum(frequencies) / self.sample_rate
        sub = np.sin(2 * np.pi * phase)

        envelope = np.exp(-t * 3)
        distortion = np.tanh(sub * 3 ) * envelope

        return self._as_signal(distortion)
    

class RiserSweep(SignalGenerator):
    name = "Riser Sweep"
    plugin_id = "riser-sweep"
    arg_list = [
        "duration",
        "sample_rate",
    ]

    def __init__(
        self,
        duration: float = 2.0,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        from sound_arcanum.effects.lib.common import CheapDelay, AddWhiteNoise

        t = np.linspace(0, self.duration, int(self.duration * self.sample_rate))

        modulator = np.sin(2 * np.pi * 3 * t)
        carrier = np.sin(2 * np.pi * 200 * t + 50 * modulator)

        sweep = np.linspace(0.01, 1.0, len(t))
        sweeped = carrier * sweep

        sig = CheapDelay(
            AudioSignal(sweeped),
            delay_time=0.3,
            feedback=0.4
        ).get_signal()
        data = sig.safe_buffer()

        noise_sig = AddWhiteNoise(AudioSignal(data), noise_level=0.02).get_signal()
        noise = noise_sig.safe_buffer()

        return noise / np.max(np.abs(noise))
    

class MetalClang(SignalGenerator):
    name = "Metallic Clang"
    plugin_id = "metal-clang"
    arg_list = [
        "duration",
        "sample_rate",
    ]

    def __init__(
        self,
        duration: float = 0.5,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.duration = duration
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        t = np.linspace(0, self.duration, int(self.duration * self.sample_rate))

        noise = np.random.normal(0, 1, len(t))
        burst_envelope = np.exp(-t * 30)

        tone = np.sin(2 * np.pi * 650.0 * t + np.sin(2 * np.pi * 10 * t))

        clang = 0.5 * noise * burst_envelope + 0.5 * tone * burst_envelope

        data = np.tanh(clang * 3)

        return self._as_signal(data)
    

class PsyKickZap(SignalGenerator):
    name = "Psy-kick Zap"
    pluin_id = "psy-kick-zap"
    arg_list = ["sample_rate"]

    def __init__(self, sample_rate: int = DEFAULT_SAMPRATE):
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        kick = Tr808Kick(
            duration=0.25,
            bass_frequency=55.0,
            sample_rate=self.sample_rate
        ).get_signal()
        kick = kick.safe_buffer()

        t = np.linspace(0, 0.3, int(self.sample_rate * 0.3), endpoint=False)

        frequency_modulator = np.sin(2 * np.pi * 80 * t + 20 * np.sin(2 * np.pi * 60 * t))
        zap_envelope = np.exp(-t * 20)

        zap = frequency_modulator * zap_envelope

        data = np.zeros(int(self.sample_rate * 0.5))
        data[:len(kick)] += kick
        data[:len(zap)] += zap * 0.8

        data = np.tanh(data * 3)

        return self._as_signal(data)
    

