import os
import json
import time
from copy import deepcopy

import numpy as np
from pynput import keyboard

from .signal import AudioSignal
from .plugin_lib import load_from_id

C_KEYS = [
    "a",
    "w",
    "s",
    "e",
    "d",
    "f",
    "t",
    "g",
    "y",
    "h",
    "u",
    "j",
    "k",
    "o",
    "l",
    "p",
    ";",
    "'",
]
E_KEYS = [
    "a",
    "s",
    "e",
    "d",
    "r",
    "f",
    "t",
    "g",
    "h",
    "u",
    "j",
    "i",
    "k",
    "l",
    "p",
    ";",
    "[",
    "'",
]

C_RANGE = range(-9, 9)
E_RANGE = range(-5, 13)



def main(base_frequency: float = 440.0, in_key="c", process_chain: list = []):
    if len(process_chain) == 0:
        raise ValueError("Process chain is empty.")
    initial_man = process_chain.pop(0)
    keys = []
    signals = []
    kwargs = initial_man["kwargs"]
    if "frequency" not in kwargs:
        raise ValueError("Missing frequency parameter in kwargs for initial manifest.")
    if in_key.lower().strip() not in ("c", "e"):
        raise ValueError(f"invalid arg: {in_key}")
    elif in_key.lower().strip() == "c":
        keys[:] = C_KEYS[:]
        note_range = C_RANGE
    elif in_key.lower().strip() == "e":
        keys[:] = E_KEYS[:]
        note_range = E_RANGE
    
    plugin_class = load_from_id(initial_man["plugin_id"])
    if not plugin_class:
        raise RuntimeError("Failed to load initial plugin.")
    for i in note_range:
        factor = 2 ** (i / 12.0)
        freq = base_frequency * factor
        new_manifest = initial_man.copy()
        new_manifest["kwargs"]["frequency"] = freq
        kwargs = new_manifest["kwargs"]

        plugin = plugin_class(**kwargs)
        signals.append(plugin.get_signal())

    for man in process_chain:
        next_effect = load_from_id(man["plugin_id"])
        for i in range(len(signals)):
            old_sig = signals[i]
            kwargs = man["kwargs"]
            kwargs["signal"] = old_sig.copy()
            effect = next_effect(**kwargs)

            signals[i] = effect.get_signal()
        
    key_sigs = dict(zip(keys, signals))

    def on_press(key):
        try:
            signal = key_sigs.get(key.value)
            if signal:
                signal.play()
        except Exception:
            pass
        return
    
    def on_release(key):
        try:
            if key.value in key_sigs:
                key_sigs[key.value].stop()
        except:
            pass

    try:
        with keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        ) as listener:
            listener.join()
    except KeyboardInterrupt:
        # 
        print("Exiting.")


if __name__ == "__main__":
    process_chain = [
        {
            "signal_uid": None,
            "kwargs": {
                "frequency": 220.0,
                "duration": 0.7,
                "amplitude": 0.8,
                "sample_rate": 48000,
            },
            "type": "generator",
            "plugin_id": "square-wave",
            "chain_idx": 0,
        }
    ]
    main(
        base_frequency=220.0,
        in_key="c",
        process_chain=process_chain
    )