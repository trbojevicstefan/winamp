import argparse
import json
import sys
from typing import Dict, List, Optional

import requests
from yt_dlp import YoutubeDL

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v={video_id}"


def search_videos(api_key: str, query: str, max_results: int = 5) -> List[Dict[str, str]]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key,
    }
    response = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    items = []
    for item in data.get("items", []):
        video_id = item["id"].get("videoId")
        snippet = item.get("snippet", {})
        if not video_id:
            continue
        items.append(
            {
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "published": snippet.get("publishedAt", ""),
            }
        )
    return items


def extract_audio_stream(video_id: str) -> Optional[Dict[str, str]]:
    url = YOUTUBE_VIDEO_URL.format(video_id=video_id)
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    if not info:
        return None
    stream_url = info.get("url")
    title = info.get("title", "")
    duration = info.get("duration", 0)
    return {"url": stream_url, "title": title, "duration": duration}


def write_m3u(entry: Dict[str, str]) -> str:
    duration = int(entry.get("duration") or -1)
    title = entry.get("title") or "YouTube Audio"
    stream_url = entry.get("url")
    m3u_lines = ["#EXTM3U", f"#EXTINF:{duration},{title}", stream_url]
    return "\n".join(m3u_lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search YouTube for audio-only playback and optionally produce an M3U"
            " playlist entry that Winamp can open as a stream."
        )
    )
    parser.add_argument("query", help="Search query text for YouTube")
    parser.add_argument(
        "--api-key",
        default="AIzaSyAd4AJE-8_QtKYc_o_Fj5e9HiUfg_uW14o",
        help="YouTube Data API key to use for searches (defaults to provided key)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of search results to retrieve",
    )
    parser.add_argument(
        "--index",
        type=int,
        default=1,
        help="One-based index of the search result to extract the audio stream for",
    )
    parser.add_argument(
        "--write-m3u",
        metavar="PATH",
        help="Optional path to write an .m3u playlist entry for the selected stream",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the selected stream metadata as JSON for scripting",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        results = search_videos(args.api_key, args.query, max_results=args.max_results)
    except requests.HTTPError as exc:
        sys.stderr.write(f"YouTube search failed: {exc}\n")
        sys.exit(1)

    if not results:
        sys.stderr.write("No results found.\n")
        sys.exit(1)

    if args.index < 1 or args.index > len(results):
        sys.stderr.write(
            f"Result index {args.index} is out of range (1-{len(results)}).\n"
        )
        sys.exit(1)

    selection = results[args.index - 1]
    stream = extract_audio_stream(selection["video_id"])
    if not stream:
        sys.stderr.write("Could not extract audio stream.\n")
        sys.exit(1)

    stream_entry = {**selection, **stream}

    print("Selected YouTube track:")
    print(f"  Title   : {stream_entry['title']}")
    print(f"  Channel : {stream_entry['channel']}")
    print(f"  Video ID: {stream_entry['video_id']}")
    print(f"  Stream  : {stream_entry['url']}")

    if args.write_m3u:
        m3u_content = write_m3u(stream_entry)
        with open(args.write_m3u, "w", encoding="utf-8") as handle:
            handle.write(m3u_content + "\n")
        print(f"Wrote M3U playlist entry to {args.write_m3u}")

    if args.json:
        print(json.dumps(stream_entry, indent=2))


if __name__ == "__main__":
    main()
