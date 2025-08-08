from typing import Optional, Iterable, Literal

import os
import json
import pickle
from datetime import datetime

from sound_arcanum.base.signal import AudioSignal, LOG, DEFAULT_SAMPRATE


BASE_PATH = os.path.abspath(os.getcwd())


class PluginMixin:
    name: str = "Plugin"
    plugin_id: str = "plugin"
    plugin_type: Optional[Literal["generator", "effect"]] = None
    arg_list: Iterable[str] = []

    def _process(self) -> AudioSignal:
        raise NotImplementedError()
    
    def get_signal(self) -> Optional[AudioSignal]:
        signal = None
        try:
            signal = self._process()
        except Exception as err:
            LOG.error(f"Plugin failed to process signal -> {err}")
        return signal
    
    def save_plugin(
        self,
        output: str = BASE_PATH,
        out_format: Literal["binary", "json"] = "json"
    ) -> bool:
        try:
            output = os.path.abspath(output)
            if not os.path.isdir(output):
                raise FileNotFoundError(f"'{output}' is not a valid directory!")
        except Exception as err:
            LOG.error(f"Error saving {self.plugin_id} instance as {out_format}, dest: {output}\nError: {err}")
            return False
        
        now = datetime.now().strftime("%Y-%m-%d")
        fmt = out_format.lower().strip()
        if fmt not in ("binary", "json"):
            LOG.error(f"Cannot save plugin to unknown format: '{out_format}'.")
            return False
        if fmt == "binary":
            return self._export_binary(output, now)
        elif fmt == "json":
            return self._export_json(output, now)
        LOG.warning(f"Did not finish exporting {self.plugin_id} instance. Invalid arguments detected.")
        return False
    
    def _export_json(self, dest: str, dt: str) -> bool:
        filename = f"{self.plugin_type}_{self.plugin_id}_{dt}.json"
        path = os.path.join(dest, filename)
        try:
            with open(path, "w") as file:
                data = {
                    "plugin_id": self.plugin_id,
                    "kwargs": {},
                    "type": self.plugin_type,
                    "signal_uid": getattr(self, "signal_uid", None),
                }
                for attr in self.arg_list:
                    data["kwargs"][attr] = getattr(self, attr, None)
                
                file.write(json.dumps(data))
            return True
        except Exception as err:
            LOG.error(err)
            return False
        
    def _export_binary(self, dest: str, dt: str) -> bool:
        filename = f"{self.plugin_type}_{self.plugin_id}_{dt}.arc"
        path = os.path.join(dest, filename)
        try:
            with open(path, "wb") as handle:
                handle.write(pickle.dumps(self))
            return True
        except Exception as err:
            LOG.error(err)
            return False
        