import os
import json


from sound_arcanum.generators.lib import waves, drums, complex
from sound_arcanum.effects.lib import common, convolution, stereo, impulse_response


plugins = {
    "sine-wave": waves.SineWave,
    "triangle-wave": waves.TriangleWave,
    "sawtooth-wave": waves.SawtoothWave,
    "square-wave": waves.SquareWave,
    "tr808-kick" : drums.Tr808Kick,
    "tr808-snare": drums.Tr808Snare,
    "tr808-hihat": drums.Tr808HiHat,
    "industrial-kick": drums.IndustrialKick,
    "industrial-snare": drums.IndustrialSnare,
    "glitch-hihat": drums.GlitchHiHat,
    "sub-bass-glide": drums.SubBassGlide,
    "riser-sweep": drums.RiserSweep,
    "metal-clang": drums.MetalClang,
    "psy-kick-zap": drums.PsyKickZap,
    "ambient-pad": complex.AmbientPad,
    "pluck-synth": complex.PluckSynth,
    "cyber-bass": complex.CyberBass,
    "modulated_sine": complex.ModulatedSine,
    "ramp-modulation-sine": complex.RampModulation,
    "phase-chord": complex.PhaseChord,
    "hard-clip": common.HardClip,
    "soft-clip": common.SoftClip,
    "bit-crush": common.BitCrush,
    "down-sample": common.DownSample,
    "comb-filter": common.CombFilter,
    "tremolo": common.Tremolo,
    "reverse-audio": common.ReverseAudio,
    "low-pass=filter": common.LowPassFilter,
    "cheap-delay": common.CheapDelay,
    "white-noise": common.AddWhiteNoise,
    "lfo": common.LowFreqOscillator,
    "ring-modulator": common.RingModulator,
    "volume-envelope": common.VolumeEnvelope,
    "high-pass-filter": common.HighPassFilter,
    "phaser": common.PhaserEffect,
    "auto-wah": common.AutoWah,
    "chorus": common.ChorusEffect,
    "vibrato": common.Vibrato,
    "gain-boost": common.GainBoost,
    "fade-out": common.FadeOut,
    "convolution-reverb": convolution.ConvolutionReverb,
    "cabinet-impulse-filter": convolution.CabinetImpulseFilter,
    "custom-convolution": convolution.CustomConvolution,
    "stereo-convolution-reverb": stereo.StereoConvolutionReverb,
    "stereo-ping-pong": stereo.StereoDelay,
    "stereo-balance": stereo.StereoBalance,
}


def load_from_id(plugin_id: str):
    plugin_class = plugins.get(plugin_id, None)
    return plugin_class


