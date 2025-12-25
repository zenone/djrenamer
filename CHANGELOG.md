# CHANGELOG.md

All notable changes between the **original script (`batch_rename.py`)** and the **current DJ-grade implementation (`djrenamer.py`)** are documented here.

---

## DJ-Grade Rewrite

### 🔥 OVERVIEW

This release represents a **ground-up evolution** from a basic batch-renaming utility into a **production-ready DJ library management tool**.

The original script:
- Focused primarily on filename renaming
- Relied on limited metadata
- Had no album awareness, DJ tooling considerations, or safety mechanisms

The new implementation:
- Treats filenames and metadata as **separate but complementary systems**
- Aligns with **Rekordbox / CDJ-3000 real-world usage**
- Introduces safety, extensibility, and future-proofing

---

## 🚀 Major Features Added

### DJ-Oriented Filename Strategy
**NEW**
- Standardized filename format:
  ```
  Artist - Title (Mix) [Key BPM].mp3
  ```
- Optional inclusion of:
  - Musical Key
  - BPM
  - Mix / Version info
- Illegal filesystem characters are safely stripped
- Filenames are length-limited to avoid USB / filesystem edge cases

**WHY**
- Optimized for scanning on CDJs, USBs, and Finder
- Human-readable even when Rekordbox databases break

---

### Album & EP Awareness
**NEW**
- Automatic album/EP detection based on:
  - Consistent album tags
  - Presence of track numbers
- Automatic track number prefixing:
  ```
  01 Artist - Track.mp3
  ```
- User overrides:
  - `--force-album`
  - `--no-album`

**OLD**
- No album concept
- Track order was lost during renames

---

### Deep Metadata Parsing
**IMPROVED**
- Reads from:
  - Standard ID3 frames (`TPE1`, `TIT2`, `TALB`, `TRCK`, `TBPM`, `TKEY`)
  - DJ-standard custom frames (`TXXX:BPM`, `TXXX:INITIALKEY`, `TXXX:MIXNAME`, etc.)
- Filename parsing as fallback when tags are missing

**OLD**
- Limited metadata handling
- No fallback strategy

---

### Metadata Normalization & Cleanup
**NEW**
- Optional `--clean-tags` mode
- Normalizes:
  - Whitespace
  - Smart quotes
  - `feat.` formatting
- Writes:
  - `TBPM` (BPM)
  - `TKEY` (optionally Camelot)
  - `TRCK` (proper formatting)
- Preserves MusicBrainz IDs

**OLD**
- No metadata writing or cleanup

---

### Musical Key Intelligence
**NEW**
- Supports:
  - Traditional keys (`Am`, `C#`, etc.)
  - Camelot notation (`8A`, `9B`)
- Accurate Camelot ↔ musical key mapping
- Optional Camelot writing via `--write-key-camelot`

**OLD**
- No key awareness

---

### BPM Handling
**NEW**
- BPM parsed safely from multiple tag variants
- Validated BPM range (30–250)
- Optional deterministic writing to `TBPM`

**OLD**
- No BPM support

---

### Online Metadata Recovery (Advanced)
**NEW**
- Optional Picard-style recovery using:
  - Chromaprint (`fpcalc`)
  - AcoustID
  - MusicBrainz
- Rate-limited (1 req/sec)
- Fully opt-in via `--online`

**OLD**
- No online enrichment

---

### Safety & Reliability Improvements

**NEW**
- `--dry-run` mode (no file changes)
- Collision-safe renaming:
  ```
  Track.mp3
  Track (2).mp3
  ```
- Never overwrites files
- Explicit verbosity levels (`-v`, `-vv`)

**OLD**
- Risk of silent overwrites
- No preview mode

---

### Performance & Scalability

**NEW**
- Parallel processing using `ThreadPoolExecutor`
- Thread-safe global rate limiter for APIs
- Efficient directory grouping

**OLD**
- Single-threaded
- Not scalable for large libraries

---

### CLI & UX Improvements

**NEW**
- Full argparse-based CLI
- Clear flags for every major behavior
- Mutually exclusive album mode controls
- Descriptive help text

**OLD**
- Minimal CLI surface
- Limited configurability

---

### Architecture & Code Quality

**IMPROVED**
- Structured into logical sections:
  - Tag handling
  - Naming logic
  - Online enrichment
  - CLI orchestration
- Strong typing via `@dataclass`
- Defensive error handling
- Explicit documentation and docstrings

**OLD**
- Monolithic script
- Limited error handling
- Minimal documentation

---

## 🧪 Testing & Maintainability

**NEW**
- Designed for unit-testability:
  - BPM parsing
  - Key conversion
  - Filename safety
  - Album heuristics
- Centralized helpers for future extension

**OLD**
- No clear test seams

---

## ⚠️ Breaking Changes

- Filenames will **change format**
- Metadata may be **written back to files** when enabled
- Online mode requires:
  - External tools
  - API keys
- Users should **always dry-run first**

---

## ✅ Migration Guidance

Recommended upgrade path:

```bash
# 1. Preview everything
python3 djrenamer.py ~/Music/Incoming --recursive --dry-run -vv

# 2. Apply safely
python3 djrenamer.py ~/Music/Incoming --recursive --clean-tags --write-bpm --write-key-camelot
```

---

## 🧠 Final Notes

This rewrite intentionally shifts the script from:
> “batch renaming helper”

to:

> “DJ library integrity tool”

Every breaking change was made in service of:
- Longevity
- Portability
- Professional DJ workflows

---

End of changelog.
