# Psytrance / Goa Trance MIDI Generator

A comprehensive MIDI generator for psytrance and goa trance production, creating full arrangements with **47 tracks** across 5 instrument categories.

## Generated Files

### Full Arrangements (47 tracks each)
| File | Style | BPM | Bars | Scale | Size |
|------|-------|-----|------|-------|------|
| `psytrance_145bpm_A_8bar.mid` | Standard Psytrance | 145 | 8 | Double Harmonic (Byzantine) | 14.5 KB |
| `psytrance_148bpm_E_8bar.mid` | Psytrance | 148 | 8 | Phrygian | 14.5 KB |
| `psytrance_150bpm_F#_4bar.mid` | Fast Psy | 150 | 4 | Harmonic Minor | 7.9 KB |
| `goa_140bpm_A_16bar.mid` | Goa Trance | 140 | 16 | Double Harmonic | 27.8 KB |
| `darkpsy_152bpm_D_8bar.mid` | Darkpsy | 152 | 8 | Harmonic Minor | 14.5 KB |
| `prog_138bpm_G_8bar.mid` | Progressive | 138 | 8 | Natural Minor | 14.5 KB |

### Stem Groups (for mixing)
| File | Tracks | Notes | Contents |
|------|--------|-------|----------|
| `STEMS_Kick.mid` | 3 | 96 | Main, Sub, Click layers |
| `STEMS_Bass.mid` | 6 | 332 | Sub, Main, FM, Mid, High, Reso |
| `STEMS_Percussion.mid` | 14 | 507 | All drums & percussion |
| `STEMS_Leads.mid` | 8 | 384 | Leads, sequences, acid line |
| `STEMS_Pads_FX.mid` | 11 | 177 | Pads, atmospheres, FX, vocals |

### Channel Groups (per variation, 4 files)
| Channel | Contents | Typical DAW Routing |
|---------|----------|---------------------|
| `channel_01.mid` | All bass tracks (6) | Bass bus / synth rack |
| `channel_02.mid` | All lead/sequence tracks (10) | Lead bus |
| `channel_03.mid` | All pad/FX tracks (12) | Pad/FX bus |
| `channel_10.mid` | All drum/percussion (19) | Drum rack (Ch 10) |

## Track Breakdown (47 Tracks)

### Kick & Bass (9 tracks) - The Foundation
| Track | Purpose | Pattern |
|-------|---------|---------|
| `Kick_Main` | Primary kick | 4-on-floor, accented 1&3 |
| `Kick_Sub` | Sub-bass reinforcement | Slightly delayed, longer decay |
| `Kick_Click` | Attack transient | Ultra-short click layer |
| `Bass_Sub` | Sub-bass (root) | Whole notes, -1 octave |
| `Bass_Main` | Rolling bassline | 16th notes, classic psy pattern |
| `Bass_FM` | FM texture | 8th notes, metallic timbre |
| `Bass_Mid` | Mid harmonics | Offbeat accents |
| `Bass_High` | High harmonics | Polyrhythmic 3/16 pattern |
| `Bass_Reso` | Resonance accents | Filter sweep moments |

### Percussion (16 tracks)
| Track | Purpose |
|-------|---------|
| `HH_Closed_Main` | 16th note hats, accented groove |
| `HH_Closed_Ghost` | 32nd note ghost hats |
| `HH_Open` | Open hats on 2 & 4 |
| `HH_Ride` | Ride pattern (2nd half) |
| `Snare_Main` | Snare on 2 & 4 |
| `Snare_Ghost` | End-of-bar rolls |
| `Clap_Main` / `Clap_Layer` | Layered claps |
| `Perc_Shaker` | 16th note shaker groove |
| `Perc_Tambourine` | 16ths on 2 & 4 |
| `Perc_Conga_Low/High` | Conga patterns |
| `Perc_Timbale` / `Perc_Bongo` | Latin percussion |
| `Crash_Main` / `Crash_FX` | Section markers |

### Leads & Sequences (10 tracks)
| Track | Purpose |
|-------|---------|
| `Lead_Main` | Hypnotic lead melody |
| `Lead_Layer` / `Lead_Octave` / `Lead_Reso` | Harmony layers |
| `Seq_Main_16th` | **Core driving sequence** (16th notes) |
| `Seq_Main_8th` | 8th note counter-sequence |
| `Seq_Counter` | Offbeat counter-melody |
| `Seq_Arp` | Fast 32nd note runs |
| `Seq_Pluck` | Short pluck stabs |
| `Acid_Line` | 303-style squelch line |

### Pads, Atmospheres & FX (12 tracks)
| Track | Purpose |
|-------|---------|
| `Pad_Main` / `Pad_Warm` / `Pad_Evolve` / `Pad_Dark` | Evolving chord pads |
| `Atmo_Space` / `Atmo_SciFi` / `Atmo_Voice` | Long atmospheric textures |
| `FX_Riser` | Ascending pitch risers (every 4 bars) |
| `FX_Downer` | Descending downers |
| `FX_Impact` | Section impact hits |
| `Vocal_Chop` | Rhythmic vocal chops |
| `Glitch_Perc` | Random glitch clicks |

## Scripts & Usage

### 1. `scripts/generate_full.py` — **Main CLI (Recommended)**
Generates complete arrangements with stems, channels, and optional ollama integration.

```bash
cd /home/baboon/psytrance-generator
source ~/env/bin/activate

# --- Show all available options ---
python scripts/generate_full.py --help

# --- Generate all 6 standard variations (psytrance, goa, darkpsy, prog) ---
python scripts/generate_full.py --all

# --- Generate all variations WITH ollama patterns ---
python scripts/generate_full.py --all --ollama

# --- Custom single track ---
python scripts/generate_full.py \
    --bpm 145 \
    --bars 8 \
    --root A \
    --scale double_harmonic \
    --seed 12345 \
    --name my_custom_track

# --- Custom with ollama ---
python scripts/generate_full.py \
    --bpm 152 \
    --root D \
    --scale harmonic_minor \
    --seed 99999 \
    --name darkpsy_forest \
    --ollama

# --- Random seed (different every run) ---
python scripts/generate_full.py \
    --bpm 148 \
    --root E \
    --scale phrygian \
    --seed $(date +%s) \
    --name psy_$(date +%s)

# --- Custom output directory ---
python scripts/generate_full.py --all --output-dir /path/to/output

# --- Use the Monte Carlo development for complex groove/pattern variations ---
python scripts/generate_full.py --bpm 145 --bars 8 --seed 12345 \
    --name mc_variation --monte-carlo

# --- Export selected track groups alongside the full arrangement ---
python scripts/generate_full.py --bpm 145 --bars 8 --seed 42 \
    --name lead_pad_mc --monte-carlo --tracks lead,pad
```

**Output Structure (per variation):**
```
midi/
├── full/           # Complete 47-track arrangement
│   └── {name}.mid
├── stems/          # 5 stem groups
│   └── {name}_STEMS_{Kick,Bass,Percussion,Leads,Pads_FX}.mid
├── channels/       # 4 channel groups
│   └── {name}_channel_{01,02,03,10}.mid
├── tracks/         # Selected groups/tracks (when --tracks is used)
│   └── {name}_{lead,pad,bass}.mid
└── ollama/         # Ollama patterns (if --ollama)
    └── ollama_{kick_bass,percussion,lead_sequence,pads_atmosphere,full_arrangement}.mid
```

**Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `--bpm` | 145 | Tempo (BPM) |
| `--bars` | 8 | Number of bars (4, 8, 16) |
| `--root` | A | Root note (A, A#, Bb, B, C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab) |
| `--scale` | double_harmonic | Scale (minor, phrygian, harmonic_minor, double_harmonic, minor_pentatonic) |
| `--seed` | random | Random seed (integer, or omit for time-based) |
| `--name` | auto | Output name prefix |
| `--ollama` | false | Also generate with Musician-Llama |
| `--monte-carlo` | false | Apply Sobol parameter exploration, MCMC groove sampling, density changes, and scale-safe melodic mutations |
| `--all` | false | Generate all 6 standard variations |
| `--tracks` | none | Comma-separated categories or exact track names; exports files under `tracks/` |
| `--output-dir` | ./midi | Output directory |

---

### 2. `scripts/generate.py` — Simple Custom Generator
Lightweight single-file generator without stems/channels.

```bash
# Basic usage
python scripts/generate.py --bpm 145 --bars 8 --root A --scale double_harmonic --seed 42 -o my_track.mid

# Quick random
python scripts/generate.py --bpm 150 --root F# --scale harmonic_minor --seed $RANDOM -o fast.mid

# Enable Python Monte Carlo groove and pattern variations
python scripts/generate.py --bpm 145 --bars 8 --seed 42 \
    --monte-carlo -o mc_track.mid

# Help
python scripts/generate.py --help
```

**Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `-o, --output` | psytrance_custom.mid | Output filename |
| `--bpm` | 145 | Tempo |
| `--bars` | 8 | Number of bars |
| `--root` | A | Root note |
| `--scale` | double_harmonic | Scale |
| `--seed` | random | Random seed |
| `--monte-carlo` | false | Enable Python Sobol/MCMC MIDI variations |

---

### 3. `scripts/psytrance_generator.py` — Core Engine (Python API)
Use directly in Python for maximum control.

```python
from scripts.psytrance_generator import (
    generate_psytrance_midi, PsyConfig, generate_stem_groups
)

# Generate single arrangement
config = PsyConfig(bpm=145, bars=8, tpq=480)
score = generate_psytrance_midi(
    output_path="my_track.mid",
    config=config,
    root_note='A',
    scale='double_harmonic',
    seed=12345
)

# Generate stem groups programmatically
from pathlib import Path
generate_stem_groups(Path("midi/stems"), seed=12345)

# Access the pattern generator for custom patterns
from scripts.psytrance_generator import PsyPatternGenerator
gen = PsyPatternGenerator(config, root=57, scale_name='phrygian', seed=42)
# gen.gen_bass_main(track), gen.gen_seq_16th(track), etc.
```

**PsyConfig Parameters:**
```python
PsyConfig(
    bpm=145,        # Tempo
    bars=8,         # Number of bars
    tpq=480,        # Ticks per quarter (resolution)
    swing=0.0       # Swing amount (psytrance = 0.0)
)
```

**Available Scales:**
```python
'minor'              # Natural minor: 1 2 b3 4 5 b6 b7
'phrygian'           # Phrygian: 1 b2 b3 4 5 b6 b7
'harmonic_minor'     # Harmonic minor: 1 2 b3 4 5 b6 7
'double_harmonic'    # Byzantine: 1 b2 3 4 5 b6 7 (classic Goa)
'minor_pentatonic'   # Minor pentatonic: 1 b3 4 5 b7
```

---

### 4. `scripts/ollama_integration.py` — Ollama Musician-Llama
Generate patterns using the local ollama model.

```bash
# Direct Python usage
python -c "
from scripts.ollama_integration import generate_all_categories_ollama
from pathlib import Path
generate_all_categories_ollama(Path('midi/ollama'), bars=8, bpm=145, seed=42)
"

# Or via generate_full.py --ollama (recommended)
python scripts/generate_full.py --bpm 145 --bars 8 --seed 42 --ollama
```

**What it generates (5 categories):**
| Category | Description | Typical Notes |
|----------|-------------|---------------|
| `kick_bass` | Kick + rolling bass | ~100 |
| `percussion` | Hats, snares, shakers | ~150 |
| `lead_sequence` | Leads, sequences, acid | ~30 |
| `pads_atmosphere` | Pads, atmospheres, FX | ~10 |
| `full_arrangement` | Everything combined | ~50 |

**Note:** Ollama output is experimental — model outputs raw tokens that are parsed and scaled. Quality varies; algorithmic generator is production-ready.

---

## Quick Start Examples

### Generate Everything (Recommended First Run)
```bash
cd /home/baboon/psytrance-generator
source ~/env/bin/activate
python scripts/generate_full.py --all
```
Creates 6 variations × (1 full + 5 stems + 4 channels) = **60 MIDI files**

### Generate for Specific Subgenre
```bash
# Goa Trance (16 bars, slower, double harmonic)
python scripts/generate_full.py --bpm 140 --bars 16 --root A --scale double_harmonic --name goa_journey

# Darkpsy/Forest (fast, harmonic minor)
python scripts/generate_full.py --bpm 152 --bars 8 --root D --scale harmonic_minor --name dark_forest

# Progressive (slower, natural minor)
python scripts/generate_full.py --bpm 138 --bars 8 --root G --scale minor --name prog_morning
```

### Batch Generate Variations
```bash
# 10 different seeds for same parameters
for i in {1..10}; do
  python scripts/generate_full.py \
    --bpm 145 --bars 8 --root A --scale double_harmonic \
    --seed $RANDOM \
    --name psytrance_var$i
done
```

---

## In Your DAW

### Recommended Routing (from channel files)
```
channel_10.mid (Drums)     → Drum Rack / Battery / Superior Drummer
channel_01.mid (Bass)      → Serum/Vital/Phase Plant (Bass patches)
channel_02.mid (Leads)     → Serum/Vital (Lead/Pluck/Arp patches)
channel_03.mid (Pads/FX)   → Wavetable/Granular (Pad/FX patches)
```

### Recommended VSTs
| Category | Suggestions |
|----------|-------------|
| Kick | Kick 2, BigKick, BazzISM, layered samples |
| Bass | Serum, Vital, Phase Plant, Pigments, TB-303 emu |
| Sequences | Serum, Vital, Pigments, Rapid (with filter mod) |
| Leads | Serum, Vital, Spire, Sylenth1, Diva |
| Pads | Pigments, Falcon, Omnisphere, granular synths |
| FX | Noise generators, riser patches, convolution |

---

## Customization

### Modify Patterns
Edit `scripts/psytrance_generator.py` → `PsyPatternGenerator` class:

```python
# Example: Custom bass pattern
def gen_bass_custom(self, track: symusic.Track):
    for bar in range(self.cfg.bars):
        bar_start = bar * self.cfg.bar_ticks
        # Your pattern here
        for i in range(16):
            time = bar_start + i * self.cfg.sixteenth
            degree = your_pattern[i]
            pitch = self.scale_note(degree, -1)
            self.add_note(track, time, pitch, self.cfg.sixteenth, velocity)

# Register it
generators["Bass_Custom"] = gen_bass_custom
```

### Add New Tracks
1. Add to `TRACK_SPECS` list
2. Add generator method to `PsyPatternGenerator`
3. Register in `generators` dict

---

## Technical Details

- **Resolution**: 480 PPQ (ticks per quarter note)
- **Format**: Standard MIDI File (SMF Type 1)
- **Drum tracks**: Marked with `is_drum=True`
- **Program changes**: GM patch numbers set per track
- **Reproducible**: Seed-based randomization
- **Time signature**: 4/4 (configurable via bars)

---

## Requirements

```bash
pip install symusic

# For ollama integration (optional)
# Requires ollama server at http://69.57.210.224:11434
# with model: hf.co/mradermacher/Musician-Llama-3.2-1B-Instruct-GGUF:Q4_K_M
```

---

## Tips for Production

1. **Layer kicks**: Blend Main + Sub + Click with EQ (Sub < 60Hz, Main 60-120Hz, Click > 2kHz)
2. **Bass design**: Main bass = rolling 16ths with filter envelope (decay ~200ms)
3. **Sequence**: Seq_Main_16th is the heart — automate filter cutoff every 2 bars
4. **Sidechain**: Duck pads/atmospheres to kick (SC compressor on Ch 3)
5. **Arrangement**: 16-bar Goa for full journey, 8-bar for DJ loops
6. **Transitions**: FX_Riser/Downer/Impact mark 4/8/16 bar boundaries
7. **Mix stems**: Import stem groups for independent processing

---

## License

MIT - Free for commercial and personal use.

---

## Repository

```bash
git clone git@github.com:zapadiot/psytrance_generator.git
cd psytrance_generator
source ~/env/bin/activate
python scripts/generate_full.py --all
```
