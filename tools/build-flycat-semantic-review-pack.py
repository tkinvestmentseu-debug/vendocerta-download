from __future__ import annotations

import argparse
import csv
import html
import math
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build a small, model-reviewable FlyCat forensic pack from local 1fps/8fps evidence.")
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--triage-dir", type=Path, default=None)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--overview-step-seconds", type=float, default=5.0)
    p.add_argument("--tile-width", type=int, default=360)
    p.add_argument("--jpeg-quality", type=int, default=78)
    return p.parse_args()


def tc(seconds: float) -> str:
    ms = int(round(max(0.0, seconds) * 1000.0))
    hh, rem = divmod(ms, 3_600_000)
    mm, rem = divmod(rem, 60_000)
    ss, milli = divmod(rem, 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d}.{milli:03d}"


def load_font(size: int):
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
    ]
    for c in candidates:
        if c.exists():
            try:
                return ImageFont.truetype(str(c), size=size)
            except Exception:
                pass
    return ImageFont.load_default()


FONT = load_font(20)
SMALL = load_font(16)


def fit_image(path: Path, width: int) -> Image.Image:
    with Image.open(path) as im:
        rgb = im.convert("RGB")
        scale = width / rgb.width
        height = max(2, int(round(rgb.height * scale)))
        return rgb.resize((width, height), Image.Resampling.LANCZOS)


def label_tile(img: Image.Image, label: str, sublabel: str = "") -> Image.Image:
    footer = 50 if sublabel else 30
    out = Image.new("RGB", (img.width, img.height + footer), "black")
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    d.text((6, img.height + 4), label, fill="white", font=FONT)
    if sublabel:
        d.text((6, img.height + 27), sublabel, fill="white", font=SMALL)
    return out


def save_grid(tiles: list[Image.Image], cols: int, out_path: Path, quality: int) -> None:
    if not tiles:
        return
    w = max(t.width for t in tiles)
    h = max(t.height for t in tiles)
    rows = math.ceil(len(tiles) / cols)
    canvas = Image.new("RGB", (w * cols, h * rows), (18, 18, 18))
    for i, t in enumerate(tiles):
        x = (i % cols) * w
        y = (i // cols) * h
        canvas.paste(t, (x, y))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "JPEG", quality=quality, optimize=True, progressive=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


@dataclass
class Cue:
    start: float
    end: float
    text: str


def parse_vtt_time(value: str) -> float:
    value = value.strip().replace(",", ".")
    parts = value.split(":")
    if len(parts) == 3:
        hh, mm, ss = parts
    elif len(parts) == 2:
        hh = "0"
        mm, ss = parts
    else:
        return 0.0
    return int(hh) * 3600 + int(mm) * 60 + float(ss)


def parse_vtt(path: Path) -> list[Cue]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    cues: list[Cue] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "-->" not in line:
            i += 1
            continue
        left, right = [x.strip().split()[0] for x in line.split("-->", 1)]
        start = parse_vtt_time(left)
        end = parse_vtt_time(right)
        i += 1
        text_lines: list[str] = []
        while i < len(lines) and lines[i].strip():
            txt = re.sub(r"<[^>]+>", "", lines[i].strip())
            txt = html.unescape(txt)
            if txt:
                text_lines.append(txt)
            i += 1
        text = " ".join(text_lines).strip()
        if text:
            cues.append(Cue(start, end, text))
        i += 1
    return cues


def cue_text(cues: list[Cue], start: float, end: float, pad: float = 5.0) -> str:
    a, b = start - pad, end + pad
    chosen = [c.text for c in cues if c.end >= a and c.start <= b]
    dedup: list[str] = []
    last = None
    for t in chosen:
        if t != last:
            dedup.append(t)
        last = t
    return " ".join(dedup)[:1500]


def build_overview(root: Path, out_dir: Path, step_seconds: float, tile_width: int, quality: int) -> tuple[int, int]:
    frame_dir = root / "frames_1fps"
    rows = read_csv(root / "frame_index.csv")
    picks: list[tuple[Path, str]] = []
    last = -1e9
    for row in rows:
        sec = float(row["second"])
        if sec + 1e-6 < last + step_seconds:
            continue
        p = frame_dir / row["frame"]
        if p.exists():
            picks.append((p, row["timecode"]))
            last = sec
    sheet_dir = out_dir / "phase_overview_5s"
    sheet_count = 0
    per_sheet = 36
    for offset in range(0, len(picks), per_sheet):
        tiles = [label_tile(fit_image(p, tile_width), f"T={t}") for p, t in picks[offset:offset+per_sheet]]
        sheet_count += 1
        save_grid(tiles, 6, sheet_dir / f"overview_{sheet_count:03d}.jpg", quality)
    return len(picks), sheet_count


def build_cluster_peak_sheets(root: Path, triage: Path, out_dir: Path, tile_width: int, quality: int) -> tuple[int, int]:
    rows = read_csv(triage / "frame_clusters.csv")
    dense = root / "dense_frames_8fps"
    sheet_dir = out_dir / "cluster_peaks_6x6"
    per_sheet = 36
    sheet_count = 0
    for offset in range(0, len(rows), per_sheet):
        tiles: list[Image.Image] = []
        for row in rows[offset:offset+per_sheet]:
            p = dense / row["representative_frame"]
            label = f"{row['cluster_id']}  {row['representative_timecode']}"
            sub = f"score={row['peak_score']} cand={row['candidate_count']}"
            tiles.append(label_tile(fit_image(p, tile_width), label, sub))
        sheet_count += 1
        save_grid(tiles, 6, sheet_dir / f"peaks_{sheet_count:03d}.jpg", quality)
    return len(rows), sheet_count


def build_cluster_triplets(root: Path, triage: Path, out_dir: Path, tile_width: int, quality: int) -> tuple[int, int]:
    rows = read_csv(triage / "frame_clusters.csv")
    dense = root / "dense_frames_8fps"
    sheet_dir = out_dir / "cluster_triplets_3x6"
    per_sheet = 6  # 6 clusters x 3 frames = 18 tiles, 3 columns x 6 rows
    sheet_count = 0
    fps = 8.0
    for offset in range(0, len(rows), per_sheet):
        tiles: list[Image.Image] = []
        for row in rows[offset:offset+per_sheet]:
            cid = row["cluster_id"]
            indices = [
                ("START", int(row["start_index"])),
                ("PEAK", int(row["representative_index"])),
                ("END", int(row["end_index"])),
            ]
            for kind, idx in indices:
                p = dense / f"frame_{idx+1:07d}.jpg"
                if not p.exists():
                    # frame names are 1-based while analysis indices are 0-based; fall back to recorded peak where possible
                    if kind == "PEAK":
                        p = dense / row["representative_frame"]
                label = f"{cid} {kind}  {tc(idx/fps)}"
                tiles.append(label_tile(fit_image(p, tile_width), label))
        sheet_count += 1
        save_grid(tiles, 3, sheet_dir / f"triplets_{sheet_count:03d}.jpg", quality)
    return len(rows), sheet_count


def write_cluster_context(root: Path, triage: Path, out_dir: Path) -> tuple[int, str]:
    rows = read_csv(triage / "frame_clusters.csv")
    vtts = sorted(root.glob("*.vtt"))
    cues: list[Cue] = []
    source = ""
    if vtts:
        preferred = sorted(vtts, key=lambda p: (0 if ".en-orig." in p.name else 1 if ".en." in p.name else 2, p.name))[0]
        cues = parse_vtt(preferred)
        source = preferred.name
    out = out_dir / "cluster_context.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cluster_id","start_timecode","end_timecode","peak_timecode","peak_score","candidate_count","transcript_context"])
        for r in rows:
            a = float(r["start_second"])
            b = float(r["end_second"])
            w.writerow([
                r["cluster_id"],r["start_timecode"],r["end_timecode"],r["representative_timecode"],
                r["peak_score"],r["candidate_count"],cue_text(cues,a,b)
            ])
    return len(cues), source


def copy_small_navigation(root: Path, triage: Path, out_dir: Path) -> None:
    for src in [
        root / "manifest.json",
        root / "LOCAL_READY.md",
        root / "transcript.txt",
        triage / "forensic_summary.json",
        triage / "frame_clusters.csv",
    ]:
        if src.exists():
            shutil.copy2(src, out_dir / src.name)


def main() -> int:
    a = parse_args()
    triage = a.triage_dir or (a.root / "low_token_triage")
    if not (a.root / "_FORENSICS_DONE.txt").exists():
        raise RuntimeError("FlyCat forensic root is not complete")
    if not (triage / "frame_clusters.csv").exists():
        raise RuntimeError("Low-token triage frame_clusters.csv is missing")
    if a.output_dir.exists():
        shutil.rmtree(a.output_dir)
    a.output_dir.mkdir(parents=True, exist_ok=True)

    overview_frames, overview_sheets = build_overview(a.root, a.output_dir, a.overview_step_seconds, a.tile_width, a.jpeg_quality)
    clusters, peak_sheets = build_cluster_peak_sheets(a.root, triage, a.output_dir, a.tile_width, a.jpeg_quality)
    _, triplet_sheets = build_cluster_triplets(a.root, triage, a.output_dir, a.tile_width, a.jpeg_quality)
    cue_count, vtt_source = write_cluster_context(a.root, triage, a.output_dir)
    copy_small_navigation(a.root, triage, a.output_dir)

    summary = [
        "# FLYCAT SEMANTIC REVIEW PACK READY",
        "",
        f"overview_sampled_frames={overview_frames}",
        f"overview_6x6_sheets={overview_sheets}",
        f"clusters={clusters}",
        f"cluster_peak_6x6_sheets={peak_sheets}",
        f"cluster_triplet_3x6_sheets={triplet_sheets}",
        f"timed_vtt_cues={cue_count}",
        f"timed_vtt_source={vtt_source or 'missing'}",
        "",
        "Review order:",
        "1. phase_overview_5s sequentially for whole-video phase map",
        "2. cluster_peaks_6x6 sequentially for semantic triage",
        "3. cluster_context.csv for nearby transcript context",
        "4. cluster_triplets_3x6 only for candidate operations needing before/peak/after",
        "5. request 24fps micro extraction only for unresolved short windows",
        "",
        "No visual claim may be made from change scores alone.",
    ]
    (a.output_dir / "REVIEW_ORDER.md").write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
