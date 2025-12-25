# 🎧 DJ MP3 Renamer (djrenamer.py)

A **DJ-first MP3 renaming and metadata cleanup tool** designed for real-world workflows using:

- **Rekordbox**
- **Pioneer CDJ-3000 / XDJ gear**
- USB export + Finder browsing
- Long-term library hygiene and portability

This tool focuses on what actually matters to DJs:

- Human-readable, scan-friendly filenames
- Clean, deterministic metadata
- Album/EP ordering that *never breaks*
- Optional MusicBrainz-style identification for poorly tagged files

---

## ✨ What This Tool Does

### 1. Smart DJ-Friendly Filenames
Creates filenames like:

```
Artist - Track Title (Extended Mix) [8A 128 BPM].mp3
01 Artist - Track Title.mp3
```

Why this works:
- **Artist - Title first** → fastest scanning on CDJs & USBs
- Optional **Key + BPM** for instant context when browsing files
- **Track numbers preserved** for albums/EPs

---

### 2. Deep Metadata Reading (ID3 Best Practices)

Reads metadata from **all common DJ tag variants**, including:

- Standard ID3 frames:
  - `TPE1` (Artist)
  - `TIT2` (Title)
  - `TALB` (Album)
  - `TRCK` (Track Number)
  - `TBPM` (BPM)
  - `TKEY` (Key)

- Common DJ custom tags:
  - `TXXX:INITIALKEY`
  - `TXXX:BPM`
  - `TXXX:TEMPO`
  - `TXXX:MIXNAME`
  - `TXXX:VERSION`

If metadata is missing, it **falls back to parsing the filename** safely.

---

### 3. Album / EP Detection (Automatic)

When processing folders:

- If **all tracks share the same album tag**
- And **most tracks have track numbers**

➡️ The tool automatically treats the folder as an album and prefixes:

```
01
02
03
...
```

You can override this behavior explicitly (see examples below).

---

### 4. Optional Metadata Cleanup (Highly Recommended)

With `--clean-tags`, the tool:

- Normalizes whitespace
- Fixes smart quotes
- Standardizes `feat.` formatting
- Writes:
  - `TBPM` (BPM)
  - `TKEY` (optionally in Camelot format)
  - `TRCK` (properly formatted)
- Preserves MusicBrainz IDs when found

This ensures **future-proof libraries** across tools and years.

---

### 5. Optional Online Identification (Picard-like)

For badly tagged or unknown files:

- Uses **Chromaprint (fpcalc)** to fingerprint audio
- Queries **AcoustID**
- Resolves metadata from **MusicBrainz**

This is intentionally **opt-in**, slower, and conservative.

---

## 📦 Installation

### Requirements
- macOS (tested)
- Python 3.9+

### Install Dependencies

```bash
pip install mutagen tqdm requests
```

### Optional (for online identification)

```bash
brew install chromaprint
export ACOUSTID_API_KEY="your_acoustid_api_key"
```

---

## 🚀 Usage

### Basic Structure

```bash
python3 djrenamer.py PATH [options]
```

Where `PATH` is:
- A single `.mp3` file, or
- A folder containing MP3s

---

## 🧪 SAFEST FIRST RUN (Highly Recommended)

### Dry run on a folder (no changes made)

```bash
python3 djrenamer.py ~/Music/Incoming --recursive --dry-run -vv
```

What happens:
- Shows exactly what filenames *would* change
- No files renamed
- No metadata written

---

## 🎚️ Common Real-World Examples

### Example 1: Rename a single MP3

```bash
python3 djrenamer.py "Unknown Track.mp3"
```

Output:
```
Unknown Artist - Unknown Title.mp3
```

---

### Example 2: Rename all MP3s in a folder

```bash
python3 djrenamer.py ~/Music/NewTracks
```

---

### Example 3: Recursive folder processing

```bash
python3 djrenamer.py ~/Music/NewTracks --recursive
```

Perfect for:
- Label folders
- Beatport/Bandcamp dumps
- USB prep folders

---

### Example 4: Include Key & BPM in filenames (default)

```bash
python3 djrenamer.py ~/Music/NewTracks
```

Filename example:
```
Artist - Track Title [8A 128 BPM].mp3
```

Disable if you prefer ultra-clean names:

```bash
python3 djrenamer.py ~/Music/NewTracks --no-key-bpm
```

---

### Example 5: Clean and normalize metadata (recommended)

```bash
python3 djrenamer.py ~/Music/NewTracks --clean-tags --write-bpm --write-key-camelot
```

This will:
- Write BPM to `TBPM`
- Convert musical keys → Camelot (e.g. Am → 8A)
- Normalize Artist / Title / Album / TRCK

---

### Example 6: Force album numbering

```bash
python3 djrenamer.py ~/Music/Albums --force-album
```

Always prefixes track numbers if `TRCK` exists:

```
01 Artist - Intro.mp3
02 Artist - Main Track.mp3
```

---

### Example 7: Disable album numbering entirely

```bash
python3 djrenamer.py ~/Music/Singles --no-album
```

---

### Example 8: Online metadata recovery (advanced)

```bash
export ACOUSTID_API_KEY="your_key"

python3 djrenamer.py ~/Music/Unknown   --recursive   --online   --user-agent "YourNameDJRenamer/1.0 (email@example.com)"
```

Use this when:
- Files are badly tagged
- Artist/title missing
- You want Picard-like recovery

⚠️ **Slower** (rate-limited) by design.

---

## ⚙️ All CLI Options

```text
positional arguments:
  path                  File or folder to process

optional arguments:
  -r, --recursive        Recurse into subfolders
  --dry-run              Show changes without applying them
  -v, -vv                Increase verbosity

  --include-key-bpm      Append [Key BPM] to filenames (default)
  --no-key-bpm           Disable key/bpm in filenames

  --clean-tags           Normalize and write metadata
  --write-bpm            Write TBPM tag when BPM is known
  --write-key-camelot    Write key as Camelot (8A, 9B, etc.)

  --auto-album           Auto-detect albums (default)
  --force-album          Always prefix track numbers
  --no-album             Never prefix track numbers

  --online               Use AcoustID + MusicBrainz
  --user-agent           HTTP User-Agent for MusicBrainz
```

---

## 🧠 Recommended DJ Workflow

1. **Download tracks**
2. Move into a staging folder:
   ```
   ~/Music/Incoming
   ```
3. Dry run:
   ```bash
   python3 djrenamer.py ~/Music/Incoming --recursive --dry-run -v
   ```
4. Clean + rename:
   ```bash
   python3 djrenamer.py ~/Music/Incoming --recursive --clean-tags --write-bpm --write-key-camelot
   ```
5. Import into Rekordbox
6. Analyze, cue, export to USB

---

## ⚠️ Important Notes

- This tool **never overwrites files**
- Filename collisions automatically become:
  ```
  Track Name.mp3
  Track Name (2).mp3
  ```
- Rekordbox BPM/key analysis is *not* relied upon
- Online mode respects MusicBrainz rate limits

---

## 🛡️ Philosophy

This tool is opinionated on purpose.

It favors:
- Stability over cleverness
- Human readability over gimmicks
- DJ reality over theoretical purity

If your USB ever corrupts, Rekordbox breaks, or you switch platforms —
your library will still make sense.

---

## 🖤 Built for DJs who care about their libraries

Happy digging.
