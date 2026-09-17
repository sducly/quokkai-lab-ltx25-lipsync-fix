"""Speech placement shared by baseline and transformed conditioning."""

import math

import torch


class AudioTiming:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "trim_leading_silence": ("BOOLEAN", {"default": True}),
                "trim_trailing_silence": ("BOOLEAN", {"default": True}),
                "silence_threshold_db": (
                    "FLOAT",
                    {"default": -40.0, "min": -80.0, "max": -10.0, "step": 1.0},
                ),
                "min_keep_ms": ("INT", {"default": 20, "min": 0, "max": 200, "step": 5}),
                "silence_before": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 4.0, "step": 0.05},
                ),
                "silence_after": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 4.0, "step": 0.05},
                ),
                "safety_margin": (
                    "FLOAT",
                    {"default": 0.30, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "mux_shift_ms": (
                    "INT",
                    {"default": 0, "min": -1000, "max": 1000, "step": 10},
                ),
                "fps": ("FLOAT", {"default": 18.0, "min": 1.0, "max": 60.0, "step": 1.0}),
                "max_duration": (
                    "FLOAT",
                    {"default": 5.0, "min": 1.0, "max": 5.0, "step": 0.1},
                ),
            }
        }

    RETURN_TYPES = ("AUDIO", "AUDIO", "FLOAT", "INT", "FLOAT", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = (
        "conditioning_audio",
        "mux_audio",
        "duration",
        "frame_count",
        "speech_start",
        "effective_duration",
        "trimmed_leading",
        "trimmed_trailing",
    )
    FUNCTION = "process"
    CATEGORY = "QuokkaiLab/audio"

    @staticmethod
    def _zeros(waveform, length):
        return torch.zeros(
            (*waveform.shape[:-1], length), dtype=waveform.dtype, device=waveform.device
        )

    def process(
        self,
        audio,
        trim_leading_silence,
        trim_trailing_silence,
        silence_threshold_db,
        min_keep_ms,
        silence_before,
        silence_after,
        safety_margin,
        mux_shift_ms,
        fps,
        max_duration,
    ):
        waveform = audio["waveform"]
        sample_rate = int(audio["sample_rate"])

        mono = waveform.abs().mean(dim=tuple(range(waveform.ndim - 1)))
        threshold = 10 ** (silence_threshold_db / 20.0)
        active = mono > threshold

        start, end = 0, waveform.shape[-1]
        trimmed_leading = trimmed_trailing = 0.0

        if torch.any(active):
            indices = torch.nonzero(active, as_tuple=False).flatten()
            keep = int(round(min_keep_ms * sample_rate / 1000.0))
            if trim_leading_silence:
                start = max(0, int(indices[0].item()) - keep)
            if trim_trailing_silence:
                end = min(waveform.shape[-1], int(indices[-1].item()) + 1 + keep)
            trimmed_leading = start / float(sample_rate)
            trimmed_trailing = (waveform.shape[-1] - end) / float(sample_rate)

        waveform = waveform[..., start:end]
        raw_duration = waveform.shape[-1] / float(sample_rate)

        max_frames = int(math.floor(max_duration * fps))
        max_k = max(0, (max_frames - 1) // 8)
        max_effective = (1 + 8 * max_k) / fps

        desired = raw_duration + silence_before + silence_after + safety_margin
        overflow = max(0.0, desired - max_effective)

        cut = min(safety_margin, overflow)
        safety_margin -= cut
        overflow -= cut
        cut = min(silence_after, overflow)
        silence_after -= cut
        overflow -= cut
        cut = min(silence_before, overflow)
        silence_before -= cut
        overflow -= cut

        if overflow > 1e-6:
            raise ValueError(
                f"Trimmed TTS too long for <= {max_duration:.2f}s at {fps:.0f} fps; "
                f"shorten by about {overflow:.3f}s."
            )

        desired = raw_duration + silence_before + silence_after + safety_margin
        k = min(max_k, max(0, math.ceil((desired * fps - 1.0) / 8.0)))
        frame_count = 1 + 8 * k
        effective_duration = frame_count / fps
        duration = (8.0 * k + 1e-4) / fps if k else 0.0

        before_samples = int(round(silence_before * sample_rate))
        tail_duration = max(0.0, effective_duration - (raw_duration + silence_before))
        tail_samples = int(round(tail_duration * sample_rate))

        conditioning = torch.cat(
            [
                self._zeros(waveform, before_samples),
                waveform,
                self._zeros(waveform, tail_samples),
            ],
            dim=-1,
        )

        shift_samples = min(
            int(round(abs(mux_shift_ms) * sample_rate / 1000.0)), conditioning.shape[-1]
        )
        if shift_samples:
            zeros = self._zeros(conditioning, shift_samples)
            if mux_shift_ms > 0:
                mux = torch.cat([zeros, conditioning[..., :-shift_samples]], dim=-1)
            else:
                mux = torch.cat([conditioning[..., shift_samples:], zeros], dim=-1)
        else:
            mux = conditioning

        return (
            {"waveform": conditioning, "sample_rate": sample_rate},
            {"waveform": mux, "sample_rate": sample_rate},
            float(duration),
            int(frame_count),
            float(silence_before),
            float(effective_duration),
            float(trimmed_leading),
            float(trimmed_trailing),
        )

