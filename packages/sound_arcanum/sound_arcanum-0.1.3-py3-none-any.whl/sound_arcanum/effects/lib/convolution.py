from copy import deepcopy

import numpy as np
from scipy.signal import fftconvolve

from sound_arcanum.base.signal import AudioSignal, DEFAULT_SAMPRATE
from sound_arcanum.effects.effect import SignalEffect


class ConvolutionReverb(SignalEffect):
    name = "Convolution Reverb"
    plugin_id = "convolution-reverb"
    arg_list = ["impulse_response"]

    def __init__(
        self,
        signal: AudioSignal,
        impulse_response: np.ndarray = None
    ):
        self.impulse_response = deepcopy(impulse_response)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        convolved = fftconvolve(data, self.impulse_response, mode="full")
        convolved = convolved[:len(data)]
        return self._as_signal(convolved)
    

class CabinetImpulseFilter(SignalEffect):
    name = "Cabinet Impulse Filter"
    plugin_id = "cabinet-impulse-filter"
    arg_list = ["impulse_response"]

    def __init__(
        self,
        signal: AudioSignal = None,
        impulse_response: np.ndarray = None
    ):
        self.impulse_response = deepcopy(impulse_response)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        filtered = fftconvolve(data, self.impulse_response, mode="same")
        return self._as_signal(filtered)
    

class CustomConvolution(SignalEffect):
    name = "Custom Convolution"
    plugin_id = "custom-convolution"
    arg_list = ["kernel"]

    def __init__(
        self,
        signal: AudioSignal = None,
        kernel: np.ndarray = None
    ):
        self.kernel = deepcopy(kernel)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        output = np.convolve(data, self.kernel, mode="same")
        return self._as_signal(output)
    

    