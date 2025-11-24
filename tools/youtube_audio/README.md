# YouTube audio helper for Winamp

This helper searches YouTube using the provided Data API key, extracts the best available audio-only stream, and emits an `.m3u` playlist entry you can open in Winamp so video remains hidden.

## Usage

1. Install dependencies (Python 3.9+ recommended):

   ```bash
   pip install -r tools/youtube_audio/requirements.txt
   ```

2. Search and write an `.m3u` file for a Winamp stream:

   ```bash
   python tools/youtube_audio/youtube_audio_search.py "your search terms" --write-m3u youtube_track.m3u
   ```

   The script defaults to the supplied API key `AIzaSyAd4AJE-8_QtKYc_o_Fj5e9HiUfg_uW14o` so you can start testing immediately. Pass `--index` to choose a different result.

3. Open the generated `youtube_track.m3u` in Winamp. Only the audio stream is used, preserving normal Winamp playback controls.

Pass `--json` to emit structured metadata for scripting, or `--max-results` to widen the search.
