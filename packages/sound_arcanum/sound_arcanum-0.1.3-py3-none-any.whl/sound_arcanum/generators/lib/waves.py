import numpy as np

from sound_arcanum.base.signal import AudioSignal, DEFAULT_SAMPRATE
from sound_arcanum.generators.generator import SignalGenerator


class WaveGenerator(SignalGenerator):
    arg_list = [
        "frequency",
        "duration",
        "amplitude",
        "sample_rate",
    ]

    def __init__(
        self,
        frequency: float = 440.0,
        duration: float = 1.0,
        amplitude: float = 1.0,
        sample_rate: int = DEFAULT_SAMPRATE
    ):
        self.frequency = frequency
        self.duration = duration
        self.amplitude = amplitude
        self.sample_rate = sample_rate

    def _process(self) -> AudioSignal:
        raise NotImplementedError()
    

class SineWave(WaveGenerator):
    name = "Sine Wave"
    plugin_id = "sine-wave"

    def _process(self) -> AudioSignal:
        t = np.linspace(0, 2 * np.pi * self.duration, int(self.duration * self.sample_rate))

        data = self.amplitude * np.sin(self.frequency * t)

        return self._as_signal(data)
    

class TriangleWave(WaveGenerator):
    name = "Triangle Wave"
    plugin_id = "triangle-wave"

    def _process(self) -> AudioSignal:
        t = np.linspace(0, 2 * np.pi * self.duration, int(self.duration * self.sample_rate))
        
        data = 2 / np.pi * np.arcsin(np.sin(self.frequency * t)) * self.amplitude

        return self._as_signal(data)
    

class SawtoothWave(WaveGenerator):
    name = "Sawtooth Wave"
    plugin_id = "sawtooth-wave"

    def _process(self) -> AudioSignal:
        t = np.linspace(0, 2 * np.pi * self.duration, int(self.duration * self.sample_rate))

        data = -2 / np.pi * np.arctan(
            np.tan(np.pi / 2 - (t * np.pi / (1 / self.frequency * 2 * np.pi)))
        ) * self.amplitude

        return self._as_signal(data)
    

class SquareWave(WaveGenerator):
    name = "Square Wave"
    plugin_id = "square-wave"

    def _process(self) -> AudioSignal:
        t = np.linspace(0, 2 * np.pi * self.duration, int(self.duration * self.sample_rate))

        data = np.sin(self.frequency * t) / 2 + 0.5
        data = np.round(data) - 0.5
        data = data * self.amplitude

        return self._as_signal(data)
    