from typing import Optional, Dict, Iterable, Self, Union, List, Iterator

import os
import logging
import json
import time
import base64
import uuid
from datetime import datetime
from copy import deepcopy

import numpy as np
import sounddevice as sd
from pynput import keyboard

# from plugin_lib import load_from_id


DEFAULT_SAMPRATE: int = 48000
LOG = logging.getLogger("sound_arcanum")
# lOG.addHandler(logging)
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.INFO)

class AudioSignal:
    _data: Optional[np.ndarray] = None
    _process_chain: Optional[str] = None
    _timestamp: Optional[datetime] = None

    def __init__(self, data: np.ndarray, *args, **kwargs):
        self._data = deepcopy(data)
        del data
        process_chain = kwargs.get("process_chain", [])
        manifest = kwargs.get("manifest", None)
        if manifest:
            process_chain.append(manifest)
        
        self._process_chain = self.encode_chain(process_chain)
        self.uid = uuid.uuid4().hex
        self._timestamp = datetime.now()

    @staticmethod
    def encode_chain(manifest_data: Union[Iterable, Dict]) -> Optional[str]:
        if isinstance(manifest_data, dict):
            manifest_data = [manifest_data]
        elif not isinstance(manifest_data, list):
            try:
                manifest_data = list(manifest_data)
            except:
                return None
        try:
            json_data = json.dumps(manifest_data)
            json_data = json_data.encode("utf-8")
            b64_data = base64.b64encode(json_data)
            return b64_data.decode("utf-8")
        except Exception as err:
            LOG.error(f"Base64 encoding failed: {err}")
            return None
        
    @staticmethod
    def decode_chain(encoded_data: str) -> Optional[Union[Dict, List]]:
        data = None
        try:
            encoded = encoded_data.encode("utf-8")
            decoded = base64.b64decode(encoded)
            decoded = decoded.decode("utf-8")
            data = json.loads(decoded)
        except Exception as err:
            LOG.error(f"Base64 decoding failed: {err}")
        if data:
            if len(data) == 1:
                data = data[0]
            else:
                try:
                    data = list(data)
                except:
                    return data
        return data
    
    @property
    def process_chain(self) -> Iterator[Dict]:
        data = self.decode_chain(self._process_chain)
        if isinstance(data, dict):
            data = [data]
        for manifest in data:
            yield manifest

    @process_chain.setter
    def process_chain(self, value):
        try:
            self._process_chain = self.encode_chain(value)
        except:
            return
        
    def safe_buffer(self) -> np.ndarray:
        return deepcopy(self._data)
    
    def normalize(self) -> Self:
        data = self.safe_buffer()
        data /= np.max(np.abs(data) + 1e-9)
        self._data = deepcopy(data)
        return self
    
    def copy(self) -> Self:
        data = self.safe_buffer()
        process_chain = list(self.process_chain)
        kwargs = {
            "process_chain": process_chain,
            "manifest": None,
        }
        new_object = AudioSignal(data, **kwargs)
        return new_object
    
    def stop(self) -> None:
        sd.stop()
    
    def play(self, samplerate: Optional[int] = None) -> None:
        if not samplerate:
            sample_rate = getattr(self, "sample_rate", DEFAULT_SAMPRATE)
        else:
            sample_rate = samplerate
        sd.play(self._data, sample_rate)

    @classmethod
    def record_signal(
        cls,
        duration: float = 3.0,
        sample_rate: int = DEFAULT_SAMPRATE,
        channels: int = 2,
        countdown: float = 3.0
    ) -> Self:
        while countdown > 0.0:
            os.system("clear")
            print(f"Recording signal from microphone in -> {countdown}s")
            countdown -= 0.1
            time.sleep(0.1)
        os.system("clear")
        print(f"Recording from microphone for -> {duration}s ...")

        signal = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels
        )
        sd.wait()
        return cls(signal)
    
    # @classmethod
    # def get_octave(base_frequency: float, process_chain: list, key_range = "c"):
    #     if len(process_chain) < 1:
    #         raise ValueError("Missing proceess chain")
    #     init_manifest = process_chain.pop(0)
    #     keys = []

    #     if key_range.lower().strip() == "c":
    #         key_range = range(-9, 9)
    #         keys[:] = C_KEYS[:]
    #     elif key_range.lower().strip() == "e":
    #         key_range = range(-5, 13)
    #         keys[:] = E_KEYS[:]
    #     else:
    #         raise ValueError("Invalid key range, must be 'c' or 'e'")
        
    #     notes = []
    #     for i in key_range:
    #         factor = 2 ** (i / 12.0)
    #         freq = base_frequency * factor
    #         kwargs = init_manifest.get("kwargs", {})
    #         kwargs = init_manifest["kwargs"].copy()
    #         kwargs["frequency"] = freq

    #         plugin_class = load_from_id(init_manifest["plugin_id"])
    #         if not plugin_class:
    #             raise TypeError("Failed to load plugin")
    #         plugin = plugin_class(**kwargs)
    #         signal = plugin.get_signal()
    #         notes.append(signal)

    #     key_notes = dict(zip(keys, notes))

    #     return key_notes


# def play_synth(key_notes: dict):
#     def on_press(key):
#         try:
#             signal = key_notes.get(key.value)
#             if signal:
#                 signal.play()
#         except Exception:
#             pass
#         return 
    
#     def on_release(key):
#         try:
#             if key.value in key_notes:
#                 sd.stop()
#         except:
#             pass
    
#     with keyboard.Listener(
#         on_press=on_press,
#         on_release=on_release
#     ) as listener:
#         listener.join()

    
        
        
        

