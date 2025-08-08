from typing import Dict, Optional

import numpy as np

from sound_arcanum.base.signal import AudioSignal, LOG, DEFAULT_SAMPRATE
from sound_arcanum.base.utils import PluginMixin


class SignalEffect(PluginMixin):
    plugin_type: str = "effect"

    def __init__(
        self,
        signal: AudioSignal = None,
        *args,
        **kwargs
    ):
        self.input_signal = signal.copy()
        uid = kwargs.get("signal_uid", None)
        if uid:
            self.signal_uid = uid
        else:
            self.signal_uid = getattr(signal, "uid", None)

    @property
    def manifest(self) -> Dict:
        data = {
            "signal_uid": getattr(self, "signal_uid", None),
            "kwargs": {},
            "type": "effect",
            "plugin_id": self.plugin_id,
            "chain_idx": len(list(self.input_signal.process_chain)),
        }
        for attr in self.arg_list:
            data["kwargs"][attr] = getattr(self, attr, None)
            if isinstance(data["kwargs"][attr], np.ndarray):
                data["kwargs"][attr] = None
        return data
    
    def _as_signal(self, signal_data: np.ndarray) -> AudioSignal:
        manifest = self.manifest
        process_chain = list(self.input_signal.process_chain)
        kwargs = {
            "manifest": manifest,
            "process_chain": process_chain,
            "signal_uid": getattr(self.input_signal, "uid", None),
            "chain_idx": len(process_chain),
        }
        signal = AudioSignal(signal_data, **kwargs)
        sample_rate = getattr(self.input_signal, "sample_rate", DEFAULT_SAMPRATE)
        setattr(signal, "sample_rate", sample_rate)

        return signal.copy()
    
    
