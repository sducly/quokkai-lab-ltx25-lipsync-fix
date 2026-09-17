"""Portable audio conditioning with a separate, unprocessed soundtrack."""
import io

import numpy as np
import soundfile as sf
import torch

from .driver import make_driver
from .timing import AudioTiming


class QuokkaiLabAudioConditioning(AudioTiming):
    @classmethod
    def INPUT_TYPES(cls):
        schema = super().INPUT_TYPES()
        schema['required']['enable_fix'] = ('BOOLEAN', {'default': True})
        return schema

    def process(self, audio, enable_fix=True, **timing):
        waveform = audio['waveform']
        rate = int(audio['sample_rate'])
        if (waveform.ndim != 3 or tuple(waveform.shape[:2]) != (1, 1)
                or waveform.shape[-1] < 32 or not torch.isfinite(waveform).all()):
            raise ValueError('Use one nonempty finite mono speech clip (batch size 1).')
        if rate <= 13000:
            raise ValueError('Sample rate must exceed 13000 Hz for the 6500 Hz band-pass; use 44100 or 48000 Hz.')
        if waveform.abs().max() >= 1:
            raise ValueError('Speech must have peaks below 1.0; provide an unclipped recording.')
        if not torch.any(waveform.abs() > .01):
            raise ValueError('No speech detected above -40 dBFS.')
        if timing['silence_threshold_db'] != -40:
            raise ValueError('Keep silence_threshold_db at -40 for the validated recipe.')
        if (not all(np.isfinite(timing[k]) for k in (
                'fps', 'max_duration', 'min_keep_ms', 'silence_before',
                'silence_after', 'safety_margin', 'mux_shift_ms'))
                or timing['fps'] <= 0 or timing['max_duration'] * timing['fps'] < 1
                or any(timing[k] < 0 for k in (
                    'min_keep_ms', 'silence_before', 'silence_after', 'safety_margin'))):
            raise ValueError('Invalid timing parameters.')

        # Evaluate placement identically for both arms; never mutate the input.
        clean = super().process(audio=audio, **timing)
        if not enable_fix:
            return clean

        # FLOAT64 transport avoids introducing an extra PCM24 quantization on input.
        # PCM16/24 WAV samples loaded as float32 are represented exactly here.
        buffer = io.BytesIO()
        samples = waveform[0].detach().cpu().numpy().T.astype(np.float64)
        sf.write(buffer, samples, rate, format='WAV', subtype='DOUBLE')
        buffer.seek(0)
        transformed, driver_rate = sf.read(io.BytesIO(make_driver(buffer)),
                                          dtype='float32', always_2d=True)
        driver = {'waveform': torch.from_numpy(transformed.T.copy()).unsqueeze(0).to(
                      device=waveform.device, dtype=waveform.dtype),
                  'sample_rate': driver_rate}
        placed = super().process(audio=driver, **timing)
        if placed[2:] != clean[2:] or placed[0]['waveform'].shape != clean[0]['waveform'].shape:
            raise ValueError('Clean/conditioning placement differs; no output was produced.')
        # Only the conditioning port changes. The mux port always carries clean audio.
        return (placed[0], clean[1], *clean[2:])


NODE_CLASS_MAPPINGS = {'QuokkaiLabAudioConditioning': QuokkaiLabAudioConditioning}
NODE_DISPLAY_NAME_MAPPINGS = {'QuokkaiLabAudioConditioning': 'QuokkaiLab - Audio Conditioning Fix'}
