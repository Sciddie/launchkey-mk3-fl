"""Vital (Matt Tytel's wavetable synth): curated Device-mode pages.

Parameter names are the display names Vital gives its automatable parameters (for example "Macro 1",
"Oscillator 1 Wave Frame", "Filter 1 Cutoff", "Envelope 1 Attack"). Each entry lists the display name first and
Vital's internal parameter id as a fallback. Labels are what the Launchkey's screen shows (16 characters at most).
"""


def _osc(n, what, label):
    return (label, ("Oscillator %d %s" % (n, what), "osc_%d_%s" % (n, what.lower().replace(" ", "_"))))


def _filter(n, what, label, internal=None):
    return (label, ("Filter %d %s" % (n, what), "filter_%d_%s" % (n, internal or what.lower().replace(" ", "_"))))


def _env(n, what):
    return ("Env%d %s" % (n, what), ("Envelope %d %s" % (n, what), "env_%d_%s" % (n, what.lower())))


def _p(label, display, internal):
    return (label, (display, internal))


MAP = {
    "name": "Vital",
    "match": ("vital",),
    "pages": [
        {
            "name": "Macros",
            "pots": [
                _p("Macro 1", "Macro 1", "macro_control_1"),
                _p("Macro 2", "Macro 2", "macro_control_2"),
                _p("Macro 3", "Macro 3", "macro_control_3"),
                _p("Macro 4", "Macro 4", "macro_control_4"),
                _filter(1, "Cutoff", "F1 Cutoff"),
                _filter(1, "Resonance", "F1 Reso"),
                _p("Reverb Mix", "Reverb Mix", "reverb_dry_wet"),
                _p("Volume", "Volume", "volume"),
            ],
            "faders": [
                _osc(1, "Level", "Osc1 Level"),
                _osc(2, "Level", "Osc2 Level"),
                _osc(3, "Level", "Osc3 Level"),
                _p("Sub Level", "Sub Level", "sub_level"),
                _p("Sample Level", "Sample Level", "sample_level"),
                _p("Delay Mix", "Delay Mix", "delay_dry_wet"),
                _p("Chorus Mix", "Chorus Mix", "chorus_dry_wet"),
                _p("Dist Mix", "Distortion Mix", "distortion_mix"),
            ],
        },
        {
            "name": "Osc",
            "pots": [
                _osc(1, "Wave Frame", "Osc1 WaveFrame"),
                _osc(2, "Wave Frame", "Osc2 WaveFrame"),
                _osc(3, "Wave Frame", "Osc3 WaveFrame"),
                _osc(1, "Transpose", "Osc1 Transpose"),
                _osc(2, "Transpose", "Osc2 Transpose"),
                _osc(3, "Transpose", "Osc3 Transpose"),
                _osc(1, "Unison Voices", "Osc1 Unison"),
                _osc(1, "Unison Detune", "Osc1 Detune"),
            ],
            "faders": [
                _osc(1, "Level", "Osc1 Level"),
                _osc(2, "Level", "Osc2 Level"),
                _osc(3, "Level", "Osc3 Level"),
                _osc(1, "Tune", "Osc1 Tune"),
                _osc(2, "Tune", "Osc2 Tune"),
                _osc(3, "Tune", "Osc3 Tune"),
                _osc(2, "Unison Detune", "Osc2 Detune"),
                _osc(3, "Unison Detune", "Osc3 Detune"),
            ],
        },
        {
            "name": "Filter",
            "pots": [
                _filter(1, "Cutoff", "F1 Cutoff"),
                _filter(1, "Resonance", "F1 Reso"),
                _filter(1, "Drive", "F1 Drive"),
                _filter(1, "Mix", "F1 Mix"),
                _filter(2, "Cutoff", "F2 Cutoff"),
                _filter(2, "Resonance", "F2 Reso"),
                _filter(2, "Drive", "F2 Drive"),
                _filter(2, "Mix", "F2 Mix"),
            ],
            "faders": [
                _filter(1, "Key Track", "F1 Keytrack", "keytrack"),
                _filter(2, "Key Track", "F2 Keytrack", "keytrack"),
                _filter(1, "Blend", "F1 Blend"),
                _filter(2, "Blend", "F2 Blend"),
                _p("Dist Drive", "Distortion Drive", "distortion_drive"),
                _p("Dist Mix", "Distortion Mix", "distortion_mix"),
                _p("EQ Low Gain", "EQ Low Gain", "eq_low_gain"),
                _p("EQ High Gain", "EQ High Gain", "eq_high_gain"),
            ],
        },
        {
            "name": "Env",
            "pots": [
                _env(1, "Attack"),
                _env(1, "Decay"),
                _env(1, "Sustain"),
                _env(1, "Release"),
                _env(2, "Attack"),
                _env(2, "Decay"),
                _env(2, "Sustain"),
                _env(2, "Release"),
            ],
            "faders": [
                _env(3, "Attack"),
                _env(3, "Decay"),
                _env(3, "Sustain"),
                _env(3, "Release"),
                _p("LFO1 Freq", "LFO 1 Frequency", "lfo_1_frequency"),
                _p("LFO2 Freq", "LFO 2 Frequency", "lfo_2_frequency"),
                _p("Glide", "Portamento Time", "portamento_time"),
                _p("Vel Track", "Velocity Track", "velocity_track"),
            ],
        },
        {
            "name": "FX",
            "pots": [
                _p("Reverb Mix", "Reverb Mix", "reverb_dry_wet"),
                _p("Reverb Size", "Reverb Size", "reverb_size"),
                _p("Reverb Decay", "Reverb Decay Time", "reverb_decay_time"),
                _p("Delay Mix", "Delay Mix", "delay_dry_wet"),
                _p("Delay Fdbk", "Delay Feedback", "delay_feedback"),
                _p("Chorus Mix", "Chorus Mix", "chorus_dry_wet"),
                _p("Phaser Mix", "Phaser Mix", "phaser_dry_wet"),
                _p("Flanger Mix", "Flanger Mix", "flanger_dry_wet"),
            ],
            "faders": [
                _p("Comp Mix", "Compressor Mix", "compressor_mix"),
                _p("EQ Low Gain", "EQ Low Gain", "eq_low_gain"),
                _p("EQ Band Gain", "EQ Band Gain", "eq_band_gain"),
                _p("EQ High Gain", "EQ High Gain", "eq_high_gain"),
                _p("Delay Freq", "Delay Frequency", "delay_frequency"),
                _p("Chorus Voices", "Chorus Voices", "chorus_voices"),
                _p("Dist Drive", "Distortion Drive", "distortion_drive"),
                _p("Dist Mix", "Distortion Mix", "distortion_mix"),
            ],
        },
    ],
}
