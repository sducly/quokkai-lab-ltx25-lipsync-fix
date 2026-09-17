# Release-candidate validation

Checked on 2026-09-17. This record covers technical portability and signal
preservation. It is not a public before/after lip-sync quality demonstration.

| Check | Result |
| --- | --- |
| Baseline/fix UI graph comparison | Only fix switch and output prefix differ |
| Graph references | All links reciprocal, including nested subgraph input/output sockets |
| Content cleanup | No production character names, media filenames, private paths or workspace metadata in either graph |
| API conversion | Both UI graphs expand to 65 executable nodes with comfy-cli 1.20.0 |
| Backend registration | All executable classes available in ComfyUI 0.34.0, including the existing production installation |
| Frontend import | Both workflows opened in frontend 1.51.9 with real input selections; no node/media errors after selecting the inputs |
| Frontend/API parity | All 65 executable nodes serialize identically through the frontend and the comfy-cli converter |
| Canonical parity | Expanded generation/model/decode nodes unchanged; differences limited to public inputs/prompts, output prefix, removed unused duration, end-guide default and audio wrapper |
| Audio recipe parity | Exact sample equality against production conditioning on a generated diagnostic signal |
| Mux separation | Clean sample equality between baseline/fix; source tensor unchanged |
| Timing parity | Production-equivalent trim/padding with no trim, positive and negative mux shifts |
| Rejections | Stereo, silence, nonfinite samples, full-scale peaks, low sample rate and overlong speech rejected |
| Unit tests | 8 passed in both the initial CPU environment and the existing production Python environment |
| ComfyUI CPU execution | Both audio branches executed through LoadAudio, bundled node, CreateVideo and SaveVideo |
| CPU mux smoke outputs | Both 73 frames, 24 fps, mono 44.1 kHz, clean-audio correlation 0.999997877, zero sample lag and zero audio start offset |

The CPU export test used a generated diagnostic tone and 32 × 32 constant images.
It verified the actual clean soundtrack route and codec output without loading
LTX weights. These files are diagnostic artifacts, not publishable demo media.

Initial CPU reference environment: Windows, Python 3.12, ComfyUI 0.34.0, PyTorch
2.12.1+cu130, NumPy 1.26.4, SciPy 1.15.1, SoundFile 0.13.1. The source workflow
records frontend 1.48.7. No minimum compatible version or VRAM requirement has
been experimentally established.

The existing production environment uses Windows, Python 3.12.9, ComfyUI 0.34.0,
frontend 1.51.9, PyTorch 2.7.0+cu128, NumPy 1.26.4, SciPy 1.15.1 and SoundFile
0.13.1. The GPU is an RTX 4090 Laptop GPU with 16 GB VRAM; system RAM is 64 GB.
No software stack upgrade or weight substitution was performed for the real tests.

The two workflow JSON files, custom-node implementation and numerical dependencies
remain byte-identical to RC1. Public presentation and documentation are updated.

The author has selected a public demonstration. Results remain input-dependent;
no universal perceptual improvement is claimed. Linux/macOS installation is untested. No absent historical R&D fixture
is counted as a passed check. Verified GPU results follow below.


## Real GPU validation - initial three matched pairs

All six final MP4s executed successfully in the existing production installation.
Three existing English production scenes were used, with original clean PCM24
speech: a human character, a longer animated-character reply, and a short reply.
The same inputs, positive/negative prompts, seeds, models and generation settings
were preserved within each pair. Only the fix switch and output prefix differ.

| Case | Frames | Duration | End guide | Clean-audio correlation, baseline / fix | Audio lag, both |
| --- | ---: | ---: | --- | --- | --- |
| A - human character | 97 | 4.0417 s | Off | 0.997930 / 0.997930 | 0 samples |
| B - longer character reply | 89 | 3.7083 s | On | 0.993905 / 0.993905 | 0 samples |
| C - short reply | 49 | 2.0417 s | On | 0.995199 / 0.995199 | 0 samples |

All outputs are 576 × 1024 at 24 fps, with one mono 44.1 kHz clean soundtrack
starting at zero. All frames decoded successfully. Decoded soundtracks are
sample-identical within each pair. Correlation compares the lossy encoded audio
with its correctly trimmed/padded clean source; it is not a lip-sync score.

Cases A/B use 0.2 s leading and 0.3 s trailing silence; case C uses 0.3 s each.
The shared safety margin is 0.3 s, with the existing 8k+1 frame rule. The optional
end-image guide follows the existing scene configuration and is identical between
baseline/fix. Both stage seeds remain 42; the samplers, sigmas and BF16 weights
remain unchanged.

Three synchronized side-by-side comparisons were also produced, preserving frame
count, 24 fps, panel dimensions and the common clean audio. Raw outputs remain the
source of truth. The private media, per-scene prompts, hashes and execution records
are outside the public package. The author-selected presentation edit is now
included separately under `assets/demo/`.

One in-progress render was manually interrupted because concurrent work became
unresponsive under memory pressure. Its attempt was retained in the private
manifest; the same graph was rerun after restart. Three already completed outputs
were reused after hash checks. There were no completed renders discarded or
replaced to improve the comparison. This is not a runtime or memory benchmark.

**User review:** the human example was judged favorably, while the two animated
character baselines already worked well. A later human example also had a strong
baseline according to the user. Execution success, audio checks and matching
settings do not establish a perceptual improvement for every input.


## Additional paired tests and public presentation

Further human-speech pairs used the same validated implementation. The question
pair produced 97 frames (4.0417 s), with clean-source audio correlation 0.997886;
the frustrated statement pair produced 73 frames (3.0417 s), correlation 0.998436.
Both were 576 × 1024 at 24 fps. All raw videos and their technical comparisons
fully decoded; final decoded audio was sample-identical within each pair, with
zero audio lag. These correlations measure soundtrack preservation, not lip-sync.
Within each pair, images, clean speech, prompts, seeds and settings were identical.

During example preparation, some prompt formulations generated unwanted subtitles.
Both variants were rerun with the same revised visual-only prompt and unchanged
seeds/settings. A short repeated-call example was also rejected by the user as
insufficient to judge. This selection and prompt iteration must not be described
as an unbiased benchmark. A 113-frame human complaint pair had a baseline that the
user judged to work perfectly; it provides no evidence of a useful gain.

The complete author-approved public video includes multiple comparisons, title
cards and a QuokkaiLab outro. It is a presentation edit; the original tested video
settings above describe the generated clips, not the resolution/frame rate of the
edited demonstration. See [the video](assets/demo/quokkai-lab-fix-lip-sync.mp4).
Source recordings, local paths and internal production manifests are not bundled.

## RC2 integrity at publication

The source archive was RC2, SHA256
`2badcf2be13818c5da2ba9365509ab0f3da7e13d49be77346957bec6a5bf5e96`.
Both workflow JSON contents and every custom-node file remain byte-for-byte
identical to RC2. Workflow filenames were changed only for clear download links:
`ltx25_baseline.json` became `ltx25-baseline.json`, and `ltx25_fix.json` became
`ltx25-quokkailab-fix.json`. Documentation, the approved demo/preview, repository
hygiene files and final checksums are the publication changes. The repository's
existing MIT license is preserved. No new GPU generations or DSP modifications
were needed for publication.
