import argparse
from operator import itemgetter
from pathlib import Path
import sqlite3
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Finds the best album candidates for replacing with FLAC"
    )

    parser.add_argument("-n", type=int, default=10, help="Number of results to show")
    parser.add_argument("beets_db", help="Path to beets database")

    return parser.parse_args()


def main(num_results, beets_db_path):
    if (not beets_db_path.exists()) or (not beets_db_path.is_file()):
        print("ERROR: Invalid beets_db path")
        sys.exit(1)

    # Get connection to DB
    conn = sqlite3.connect(beets_db_path)
    c = conn.cursor()

    # Get list of albums with mp3 tracks
    paths_already_found = set()
    albums = []
    for path, album, album_artist in c.execute(
        "SELECT path, album, albumartist FROM items;"
    ):
        path = Path(path.decode("utf_8")).parent

        if path in paths_already_found:
            continue

        paths_already_found.add(path)

        num_mp3_tracks = len(list(path.glob("*.mp3")))

        if num_mp3_tracks == 0:
            continue

        albums.append((album, album_artist, path, num_mp3_tracks))

    # Sort by number of mp3 files in an album
    albums = sorted(albums, key=itemgetter(3), reverse=True)

    # Output results
    for album, album_artist, path, num_mp3_tracks in albums[:num_results]:
        print(
            f"{album}\n\tArtist: {album_artist}\n\tPath: {path}\n\tNum mp3s: {num_mp3_tracks}"
        )


if __name__ == "__main__":
    args = parse_args()
    main(args.n, Path(args.beets_db))
