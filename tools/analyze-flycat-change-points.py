from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

try:
    from skimage.metrics import structural_similarity as ssim
except Exception:
    ssim = None


@dataclass
class FrameMetric:
    index: int
    frame: str
    second: float
    global_diff: float
    viewport_diff: float
    right_diff: float
    outliner_diff: float
    edge_diff: float
    dhash_hamming: int
    ssim_delta: float
    score: float = 0.0
    candidate: bool = False


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Detect semantic change windows in FlyCat dense 8fps evidence.")
    p.add_argument("--frames-dir", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--fps", type=float, default=8.0)
    p.add_argument("--resize-width", type=int, default=320)
    p.add_argument("--quantile", type=float, default=0.92)
    p.add_argument("--min-score", type=float, default=0.012)
    p.add_argument("--merge-gap-seconds", type=float, default=0.75)
    p.add_argument("--pad-seconds", type=float, default=0.50)
    p.add_argument("--copy-representatives", action="store_true")
    return p.parse_args()


def read_gray(path: Path, width: int) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise RuntimeError(f"Cannot read image: {path}")
    h, w = image.shape
    scale = width / float(w)
    nh = max(2, int(round(h * scale)))
    return cv2.resize(image, (width, nh), interpolation=cv2.INTER_AREA)


def dhash(image: np.ndarray) -> np.ndarray:
    small = cv2.resize(image, (9, 8), interpolation=cv2.INTER_AREA)
    return (small[:, 1:] > small[:, :-1]).reshape(-1)


def hamming(a: np.ndarray, b: np.ndarray) -> int:
    return int(np.count_nonzero(a != b))


def mad(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(cv2.absdiff(a, b))) / 255.0


def crop_regions(img: np.ndarray) -> dict[str, np.ndarray]:
    h, w = img.shape
    split = int(w * 0.78)
    top = int(h * 0.35)
    return {
        "viewport": img[:, :split],
        "right": img[:, split:],
        "outliner": img[:top, split:],
    }


def edge_map(img: np.ndarray) -> np.ndarray:
    return cv2.Canny(img, 60, 140)


def robust_normalize(values: np.ndarray) -> np.ndarray:
    if len(values) == 0:
        return values
    lo = float(np.quantile(values, 0.10))
    hi = float(np.quantile(values, 0.99))
    if hi <= lo + 1e-9:
        return np.zeros_like(values, dtype=np.float64)
    return np.clip((values - lo) / (hi - lo), 0.0, 1.0)


def tc(seconds: float) -> str:
    ms = int(round(seconds * 1000.0))
    hh, rem = divmod(ms, 3_600_000)
    mm, rem = divmod(rem, 60_000)
    ss, milli = divmod(rem, 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d}.{milli:03d}"


def main() -> int:
    args = parse_args()
    frames = sorted(args.frames_dir.glob("frame_*.jpg"))
    if len(frames) < 2:
        raise RuntimeError(f"Need at least 2 frames in {args.frames_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics: list[FrameMetric] = []

    prev = read_gray(frames[0], args.resize_width)
    prev_regions = crop_regions(prev)
    prev_edge = edge_map(prev)
    prev_hash = dhash(prev)

    metrics.append(FrameMetric(0, frames[0].name, 0.0, 0, 0, 0, 0, 0, 0, 0))

    for i, path in enumerate(frames[1:], start=1):
        cur = read_gray(path, args.resize_width)
        if cur.shape != prev.shape:
            cur = cv2.resize(cur, (prev.shape[1], prev.shape[0]), interpolation=cv2.INTER_AREA)
        regions = crop_regions(cur)
        edges = edge_map(cur)
        cur_hash = dhash(cur)

        ssim_delta = 0.0
        if ssim is not None:
            tiny_prev = cv2.resize(prev, (160, max(2, int(prev.shape[0] * 160 / prev.shape[1]))), interpolation=cv2.INTER_AREA)
            tiny_cur = cv2.resize(cur, tiny_prev.shape[::-1], interpolation=cv2.INTER_AREA)
            try:
                ssim_delta = max(0.0, 1.0 - float(ssim(tiny_prev, tiny_cur, data_range=255)))
            except Exception:
                ssim_delta = 0.0

        metrics.append(
            FrameMetric(
                index=i,
                frame=path.name,
                second=i / args.fps,
                global_diff=mad(prev, cur),
                viewport_diff=mad(prev_regions["viewport"], regions["viewport"]),
                right_diff=mad(prev_regions["right"], regions["right"]),
                outliner_diff=mad(prev_regions["outliner"], regions["outliner"]),
                edge_diff=mad(prev_edge, edges),
                dhash_hamming=hamming(prev_hash, cur_hash),
                ssim_delta=ssim_delta,
            )
        )
        prev, prev_regions, prev_edge, prev_hash = cur, regions, edges, cur_hash

    arrays = {
        "global": robust_normalize(np.array([m.global_diff for m in metrics], dtype=np.float64)),
        "viewport": robust_normalize(np.array([m.viewport_diff for m in metrics], dtype=np.float64)),
        "right": robust_normalize(np.array([m.right_diff for m in metrics], dtype=np.float64)),
        "outliner": robust_normalize(np.array([m.outliner_diff for m in metrics], dtype=np.float64)),
        "edge": robust_normalize(np.array([m.edge_diff for m in metrics], dtype=np.float64)),
        "hash": robust_normalize(np.array([m.dhash_hamming for m in metrics], dtype=np.float64)),
        "ssim": robust_normalize(np.array([m.ssim_delta for m in metrics], dtype=np.float64)),
    }

    scores = (
        0.22 * arrays["global"]
        + 0.28 * arrays["viewport"]
        + 0.16 * arrays["right"]
        + 0.10 * arrays["outliner"]
        + 0.10 * arrays["edge"]
        + 0.06 * arrays["hash"]
        + 0.08 * arrays["ssim"]
    )
    threshold = max(args.min_score, float(np.quantile(scores[1:], args.quantile)))
    for i, m in enumerate(metrics):
        m.score = float(scores[i])
        # Region-specific jumps matter even when global score is modest.
        region_jump = arrays["right"][i] >= 0.82 or arrays["outliner"][i] >= 0.82
        m.candidate = i > 0 and (m.score >= threshold or region_jump)

    change_csv = args.output_dir / "forensic_change_points.csv"
    with change_csv.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "index","frame","second","timecode","global_diff","viewport_diff","right_diff",
            "outliner_diff","edge_diff","dhash_hamming","ssim_delta","score","candidate"
        ])
        for m in metrics:
            w.writerow([
                m.index,m.frame,f"{m.second:.3f}",tc(m.second),f"{m.global_diff:.6f}",
                f"{m.viewport_diff:.6f}",f"{m.right_diff:.6f}",f"{m.outliner_diff:.6f}",
                f"{m.edge_diff:.6f}",m.dhash_hamming,f"{m.ssim_delta:.6f}",f"{m.score:.6f}",int(m.candidate)
            ])

    candidate_indices = [m.index for m in metrics if m.candidate]
    merge_gap = max(1, int(round(args.merge_gap_seconds * args.fps)))
    pad = max(0, int(round(args.pad_seconds * args.fps)))
    clusters: list[tuple[int,int]] = []
    if candidate_indices:
        start = last = candidate_indices[0]
        for idx in candidate_indices[1:]:
            if idx - last <= merge_gap:
                last = idx
            else:
                clusters.append((max(0, start - pad), min(len(metrics)-1, last + pad)))
                start = last = idx
        clusters.append((max(0, start - pad), min(len(metrics)-1, last + pad)))

    rep_dir = args.output_dir / "cluster_representatives"
    if args.copy_representatives:
        rep_dir.mkdir(parents=True, exist_ok=True)

    cluster_csv = args.output_dir / "frame_clusters.csv"
    with cluster_csv.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "cluster_id","start_index","end_index","start_second","end_second","start_timecode",
            "end_timecode","representative_index","representative_frame","representative_second",
            "representative_timecode","peak_score","candidate_count"
        ])
        for n, (a, b) in enumerate(clusters, start=1):
            segment = metrics[a:b+1]
            peak = max(segment, key=lambda x: x.score)
            cand_count = sum(1 for x in segment if x.candidate)
            cid = f"C{n:04d}"
            w.writerow([
                cid,a,b,f"{a/args.fps:.3f}",f"{b/args.fps:.3f}",tc(a/args.fps),tc(b/args.fps),
                peak.index,peak.frame,f"{peak.second:.3f}",tc(peak.second),f"{peak.score:.6f}",cand_count
            ])
            if args.copy_representatives:
                picks = [("start", a), ("peak", peak.index), ("end", b)]
                for label, idx in picks:
                    src = frames[idx]
                    dst = rep_dir / f"{cid}_{label}_{src.name}"
                    if not dst.exists():
                        shutil.copy2(src, dst)

    summary = {
        "frames_total": len(frames),
        "fps": args.fps,
        "duration_seconds_approx": (len(frames)-1)/args.fps,
        "candidate_frames": len(candidate_indices),
        "candidate_ratio": len(candidate_indices)/len(frames),
        "clusters": len(clusters),
        "score_threshold": threshold,
        "quantile": args.quantile,
        "ssim_available": ssim is not None,
        "regions": {
            "viewport": "left 78% of frame",
            "right": "right 22% of frame",
            "outliner": "top 35% of right 22%"
        },
        "policy": "Code-first triage only. Model review must use clusters + full 1fps phase coverage; no visual claim may be made from metrics alone."
    }
    (args.output_dir / "forensic_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
