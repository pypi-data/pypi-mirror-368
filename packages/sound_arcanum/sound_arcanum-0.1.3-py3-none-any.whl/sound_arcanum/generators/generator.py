from typing import Dict

import numpy as np

from sound_arcanum.base.signal import AudioSignal, LOG, DEFAULT_SAMPRATE
from sound_arcanum.base.utils import PluginMixin


class SignalGenerator(PluginMixin):
    plugin_type: str = "generator"

    def __init__(self, *args, **kwargs):
        uid = kwargs.get("signal_uid", None)
        idx = kwargs.get("chain_idx", None)
        if uid:
            signal_uid = uid
        if idx:
            chain_idx = idx
        
    @property
    def manifest(self) -> Dict:
        data = {
            "signal_uid": getattr(self, "signal_uid", None),
            "kwargs": {},
            "type": "generator",
            "plugin_id": self.plugin_id,
            "chain_idx": getattr(self, "chain_idx", 0),
        }
        for attr in self.arg_list:
            data["kwargs"][attr] = getattr(self, attr, None)
        
        return data
    
    def _as_signal(self, signal_data: np.ndarray) -> AudioSignal:
        manifest = self.manifest
        kwargs = {
            "signal_uid": getattr(self, "signal_uid", None),
            "chain_idx": getattr(self, "chain_idx", None),
            "manifest": manifest,
            "process_chain": [],
        }
        signal = AudioSignal(signal_data, **kwargs)
        sample_rate = getattr(self, "sample_rate", DEFAULT_SAMPRATE)
        setattr(signal, "sample_rate", sample_rate)

        return signal
    
    