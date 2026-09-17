# Matched before / after protocol

The author-selected [complete public comparison](assets/demo/quokkai-lab-fix-lip-sync.mp4)
includes multiple English speech examples and a QuokkaiLab outro. It is a
presentation edit, not a statistical benchmark. The source portraits and speech
recordings are not distributed as reusable input assets.

The protocol below lets you reproduce a matched comparison with your own inputs.
The `start.png` / `speech.wav` names in the workflows are example input names.

Prepare just two original assets:

- `start.png`: a neutral portrait with a clearly visible mouth, soft even lighting,
  plain background and a front-facing subject. Use a photo of yourself or another
  consenting participant, or an original character you have the right to publish.
  Use 9:16, preferably 576 × 1024. No video input is needed: this is image-to-video.
- `speech.wav`: a dry mono recording of **“Hello. It is good to see you today.”**
  spoken naturally in English, roughly 2–3 seconds. Record your own voice or a
  participant who agrees to public use. Export PCM16/PCM24 WAV at 44.1 or 48 kHz,
  with peaks below full scale. Do not add music or change the speed.

The positive prompt is already in both workflow files:

> A person faces the camera in a quiet room and says in English: "Hello. It is good
> to see you today." Natural lip and jaw movements follow the speech. The head
> remains mostly still. Static camera, consistent lighting.

Use the same bytes for both runs. Record SHA256 hashes of the two assets, both
workflow JSON files and all five model files. Keep the transcript, prompt, negative
prompt, both seeds (42), hardware, package versions, output names and any changes
in a demo manifest alongside the pair. Do not randomize the seed between queues.
If using optional end-frame guidance, supply the same end image and enable it
in both files; the first demonstration should leave it disabled.

Render baseline first, then fix, in the same ComfyUI session/backend. For each
output record frame count, FPS, duration, dimensions and soundtrack alignment.
The soundtrack should contain clean speech in both videos; the transformed driver
must never be the audible “after” soundtrack. Keep both raw output files.

Review normal-speed playback and the mouth/jaw during identical speech segments.
Show both videos at the same size, speed and time origin with “Baseline: clean
conditioning” and “QuokkaiLab: 70 Hz conditioning” labels. Use the common clean
soundtrack for a synchronized side-by-side presentation. Do not retime, interpolate,
select different prompts/seeds, or hide a failed baseline. Any presentation crop
must be the same for both. State if a pair shows no improvement.

Repeat with additional speakers/clips before making broader claims. A fixed seed
does not guarantee bitwise-identical results across GPU types, attention backends,
driver versions or precision settings.

Suggested caption:

> Same image, English speech, prompt, seeds and generation settings. Only the
> audio sent to LTX conditioning changes. Both soundtracks use the original speech.
> This example illustrates an empirical workaround; results vary by input.
