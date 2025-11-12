#!/usr/bin/env python3
"""
Batch-rename MP3 files using ID3 tags (artist/title).

Features:
- Thread-safe logging (file or stderr)
- Safe filename sanitization (no traversal or illegal chars)
- Deterministic collision handling: "Artist - Title.mp3", "Artist - Title (2).mp3", ...
- Verbosity levels and progress bar
- --dry-run and --workers options
- Type hints and pathlib-first implementation

Examples:
  python mp3_renamer.py /music
  python mp3_renamer.py /music -v 2 --dry-run
  python mp3_renamer.py /music -l rename.log --workers 8
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import eyed3
from tqdm import tqdm


# ----------------------------- Logging -------------------------------- #

def configure_logging(log_path: Optional[Path], verbosity: int) -> logging.Logger:
    logger = logging.getLogger("mp3_renamer")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # Console level depends on verbosity
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.ERROR if verbosity == 0 else logging.INFO)
    console.setFormatter(fmt)
    logger.addHandler(console)

    if log_path:
        fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


# -------------------------- Sanitization ------------------------------ #

_ILLEGAL_CHARS = r'[\\/:"*?<>|]'  # Windows + common POSIX no-nos

def safe_filename(text: str, max_len: int = 120) -> str:
    """Normalize and sanitize arbitrary text for safe cross-platform filenames."""
    # Normalize strange unicode
    t = unicodedata.normalize("NFKC", text or "").strip()
    # Remove control chars
    t = re.sub(r"[\x00-\x1f]", "", t)
    # Replace illegal characters with space
    t = re.sub(_ILLEGAL_CHARS, " ", t)
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip(". ").strip()
    # Fallback if everything vanished
    if not t:
        t = "untitled"
    # Trim length conservatively (leave room for suffix)
    return t[:max_len]


def build_base_name(artist: Optional[str], title: Optional[str]) -> str:
    a = safe_filename(artist or "Unknown Artist")
    t = safe_filename(title or "Unknown Title")
    return f"{a} - {t}"


def unique_path(directory: Path, stem: str, ext: str = ".mp3") -> Path:
    """
    Return a unique path in directory for stem+ext by appending (n).
    """
    candidate = directory / f"{stem}{ext}"
    if not candidate.exists():
        return candidate
    n = 2
    while True:
        candidate = directory / f"{stem} ({n}){ext}"
        if not candidate.exists():
            return candidate
        n += 1


# --------------------------- Renaming --------------------------------- #

@dataclass(frozen=True)
class RenameResult:
    src: Path
    dst: Optional[Path]
    status: str  # "renamed" | "skipped" | "error"
    message: Optional[str] = None


def derive_target(src: Path, logger: logging.Logger) -> Tuple[Optional[Path], Optional[str]]:
    """Compute the desired destination path for a file, or return a reason to skip."""
    try:
        audio = eyed3.load(src.as_posix())
        if not audio or not audio.tag:
            return None, "No ID3 tag found"
        artist = getattr(audio.tag, "artist", None)
        title = getattr(audio.tag, "title", None)

        if not artist and not title:
            return None, "Missing artist and title tags"

        stem = build_base_name(artist, title)
        dst = unique_path(src.parent, stem, ".mp3")
        if dst == src:
            return None, "Already has desired name"

        return dst, None
    except Exception as exc:
        logger.debug("Tag parse error for %s", src, exc_info=True)
        return None, f"Exception reading tags: {exc}"


def rename_one(src: Path, dry_run: bool, logger: logging.Logger) -> RenameResult:
    dst, skip_reason = derive_target(src, logger)
    if skip_reason:
        return RenameResult(src=src, dst=None, status="skipped", message=skip_reason)
    try:
        if dry_run:
            return RenameResult(src=src, dst=dst, status="renamed", message="dry-run")
        # Atomic on same filesystem
        src.rename(dst)  # raises if permission/locked
        return RenameResult(src=src, dst=dst, status="renamed")
    except Exception as exc:
        logger.error("Rename failed %s -> %s: %s", src, dst, exc, exc_info=True)
        return RenameResult(src=src, dst=dst, status="error", message=str(exc))


# ------------------------------ CLI ----------------------------------- #

def find_mp3s(root_dir: Path) -> list[Path]:
    return list(root_dir.rglob("*.mp3"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch rename MP3 files using ID3 tags (artist/title).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("root_dir", help="Root directory containing MP3 files to rename")
    parser.add_argument("-l", "--log-file", type=Path, help="Write detailed logs to this file")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=1,
                        help="0: errors only, 1: progress, 2: verbose progress")
    parser.add_argument("--dry-run", action="store_true", help="Show intended renames without changing files")
    parser.add_argument("--workers", type=int, default=8, help="Number of worker threads (I/O bound)")
    args = parser.parse_args()

    root = Path(args.root_dir)
    if not root.is_dir():
        print(f"Error: Invalid directory path: {root}", file=sys.stderr)
        return 1

    logger = configure_logging(args.log_file, args.verbosity)

    mp3s = find_mp3s(root)
    if args.verbosity >= 1:
        print(f"Scanning {root} — found {len(mp3s)} MP3 file(s)")

    renamed = skipped = errors = 0

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(rename_one, p, args.dry_run, logger) for p in mp3s]
        with tqdm(total=len(futures), disable=(args.verbosity == 0)) as pbar:
            for fut in as_completed(futures):
                res: RenameResult = fut.result()
                if res.status == "renamed":
                    renamed += 1
                    if args.verbosity == 2:
                        if res.message == "dry-run":
                            logger.info("[DRY] %s -> %s", res.src.name, res.dst.name if res.dst else "(same)")
                        else:
                            logger.info("Renamed: %s -> %s", res.src.name, res.dst.name if res.dst else "(same)")
                elif res.status == "skipped":
                    skipped += 1
                    if args.verbosity == 2:
                        logger.info("Skipped: %s (%s)", res.src.name, res.message or "reason unknown")
                else:
                    errors += 1
                    # Error already logged at error level in rename_one
                pbar.update(1)

    if args.verbosity >= 1:
        print(f"Done. Renamed: {renamed} | Skipped: {skipped} | Errors: {errors}")
        if args.dry_run:
            print("(Dry run - no files changed)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
