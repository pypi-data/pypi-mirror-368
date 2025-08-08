from typing import Callable

from copy import deepcopy

import numpy as np
from scipy.signal import fftconvolve

from sound_arcanum.base.signal import AudioSignal, DEFAULT_SAMPRATE
from sound_arcanum.effects.effect import SignalEffect
# import sound_arcanum.effects.lib.impuls`e_respnose as ir


def apply_to_stereo(sig_data: np.ndarray, func: Callable) -> np.ndarray:
    if sig_data.ndim == 1:
        return func(sig_data)
    elif sig_data.ndim == 2 and sig_data.shape[0] == 2:
        left = func(sig_data[0])
        right = func(sig_data[1])
        return np.vstack((left, right))
    else:
        raise ValueError("Invalid signal shape. Must be mono or stereo.")
    

class StereoConvolutionReverb(SignalEffect):
    name = "Stereo Convolution-reverb"
    plugin_id = "stereo-convolution-reverb"
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

        def convolve_channel(channel_data):
            return fftconvolve(
                channel_data,
                self.impulse_response,
                mode="full"
            )[:len(channel_data)]
        
        data = apply_to_stereo(data, convolve_channel)
        return self._as_signal(data)
    

class StereoDelay(SignalEffect):
    name = "Stereo Ping-pong Delay"
    plugin_id = "stereo-ping-pong"
    arg_list = [
        "delay_time",
        "feedback",
        "ping_pong",
    ]

    def __init__(
        self,
        signal: AudioSignal = None,
        delay_time: float = 0.3,
        feedback: float = 0.5,
        ping_pong: bool = True
    ):
        self.delay_time = delay_time
        self.feedback = feedback
        self.ping_pong = ping_pong
        self.sample_rate = getattr(signal, "sample_rate", DEFAULT_SAMPRATE)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()
        delay_samples = int(self.delay_time * self.sample_rate)

        if data.ndim == 1:
            data = np.vstack((data, np.zeros_like(data)))

        left, right = data[0], data[1]
        out_left = np.copy(left)
        out_right = np.copy(right)

        for i in range(delay_samples, len(left)):
            if self.ping_pong:
                out_left[i] += self.feedback * out_right[i - delay_samples]
                out_right[i] += self.feedback * out_left[i - delay_samples]
            else:
                out_left[i] += self.feedback * out_left[i - delay_samples]
                out_right[i] += self.feedback * out_right[i - delay_samples]

        return self._as_signal(np.vstack((out_left, out_right)))
    

class StereoBalance(SignalEffect):
    name = "Stereo Balance Pan"
    plugin_id = "stereo-balance"
    arg_list = ["pan"]

    def __init__(
        self,
        signal: AudioSignal = None,
        pan: float = 0.0
    ):
        self.pan = np.clip(pan, -1.0, 1.0)
        super().__init__(signal)

    def _process(self) -> AudioSignal:
        data = self.input_signal.safe_buffer()

        if data.ndim == 1:
            data = np.vstack((data, data))

        left_gain = 0.5 * (1 - self.pan)
        right_gain = 0.5 * (1 + self.pan)

        data[0] *= left_gain
        data[1] *= right_gain

        return self._as_signal(data)
    


