from typing import Optional

import numpy as np
from scipy.signal import fftconvolve, firwin

from sound_arcanum.base.signal import AudioSignal, DEFAULT_SAMPRATE
from sound_arcanum.effects.effect import SignalEffect


def exponential_decay(
    decay: float = 0.95,
    length: int = 4096
) -> np.ndarray:
    ir = decay ** np.arange(length)
    return ir / np.max(
        np.abs(ir)
    )


def comb_ir(
    delay_samples: int = 400,
    feedback: float = 0.5,
    length: int = 2048
) -> np.ndarray:
    ir = np.zeros(length)
    for i in range(0, length, delay_samples):
        ir[i] = feedback ** (i // delay_samples)
    return ir


def bandpass_ir(
    low_hz: float,
    high_hz: float,
    sample_rate: int = DEFAULT_SAMPRATE,
    numtaps: int = 512
) -> np.ndarray:
    return firwin(
        numtaps,
        [low_hz, high_hz],
        pass_zero=False,
        fs=sample_rate
    )


def diffuse_ir(
    length: int = 2048,
    decay: float = 0.9,
    seed: Optional[int] = None
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, size=length)
    envelope = decay ** np.arange(length)
    ir = noise * envelope
    return ir / np.max(np.abs(ir))


def allpass_ir(
    delay_samples: int = 100,
    gain: float = 0.5,
    length: int = 1024
) -> np.ndarray:
    ir = np.zeros(length)
    ir[0] = gain
    if delay_samples < length:
        ir[delay_samples] = -gain
    return ir


def custom_reverb_ir(
    length: int = 4096,
    early_reflections: int = 5,
    decay: float = 0.92,
    max_delay: int = 300,
    seed: Optional[int] = None
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ir = np.zeros(length)

    for _ in range(early_reflections):
        idx = rng.integers(20, max_delay)
        if idx < length:
            ir[idx] = rng.uniform(0.4, 0.9)

    tail = exponential_decay(decay=decay, length=length)
    ir += rng.normal(0, 0.02, size=length) * tail

    return ir / np.max(np.abs(ir))


