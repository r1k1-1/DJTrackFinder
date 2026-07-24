import os
import csv


def _ensure_output_folder():
    if not os.path.exists("output"):
        os.makedirs("output")


def export_txt(tracklist, filename="output/tracklist.txt"):
    _ensure_output_folder()

    with open(filename, "w", encoding="utf-8") as f:
        for track in tracklist:
            f.write(track + "\n")

    return filename


def export_csv(tracklist, filename="output/tracklist.csv"):
    _ensure_output_folder()

    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["#", "Track"])

        for i, track in enumerate(tracklist, start=1):
            writer.writerow([i, track])

    return filename
