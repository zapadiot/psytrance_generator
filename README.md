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

## Musical Theory

### Scales Used
- **Double Harmonic (Byzantine)**: `1 b2 3 4 5 b6 7` - Classic Goa sound
- **Phrygian**: `1 b2 b3 4 5 b6 b7` - Dark, Spanish flavor
- **Harmonic Minor**: `1 2 b3 4 5 b6 7` - Darkpsy/Forest
- **Natural Minor**: `1 2 b3 4 5 b6 b7` - Progressive

### Root Keys
Common psytrance keys: A, E, F#, D, G (easy for bass synthesis)

## Usage

```bash
# Generate all variations
cd /home/baboon/psytrance-generator
source ~/env/bin/activate
python scripts/psytrance_generator.py
```

### In Your DAW
1. Drag `.mid` files into your DAW (Ableton, Logic, FL Studio, Reaper, Bitwig, etc.)
2. **Route tracks to channels/ports**:
   - Tracks 0-2 → Kick drum rack (Ch 1)
   - Tracks 3-8 → Bass synths (Ch 2-4)
   - Tracks 9-24 → Drum rack / percussion (Ch 10)
   - Tracks 25-34 → Lead/Sequence synths (Ch 5-8)
   - Tracks 35-46 → Pad/FX synths (Ch 9-12)
3. Assign appropriate VSTs:
   - **Kick**: Kick 2, BigKick, or layered samples
   - **Bass**: Serum, Vital, Phase Plant, or hardware (TB-303, SH-101 style)
   - **Sequences**: Arp-friendly synths with filter modulation
   - **Leads**: Aggressive saw/square with unison
   - **Pads**: Evolving wavetable or granular synths
   - **FX**: Noise generators, riser patches

## Customization

Edit `scripts/psytrance_generator.py`:

```python
# Change scale
generate_psytrance_midi(output_path, config, 'A', 'phrygian')

# Custom config
config = PsyConfig(bpm=145, bars=8, tpq=480)

# Modify patterns in PsyPatternGenerator class
```

## Technical Details

- **Resolution**: 480 PPQ (ticks per quarter note)
- **Format**: Standard MIDI File (SMF Type 1)
- **Note channels**: All on channel 0 (route in DAW)
- **Drum tracks**: Marked with `is_drum=True`
- **Program changes**: GM patch numbers set per track
- **Reproducible**: Fixed seed (42) for consistent results

## Requirements

```bash
pip install symusic
```

## Tips for Production

1. **Layer kicks**: Blend Main + Sub + Click with EQ
2. **Bass design**: Main bass = rolling 16ths with filter envelope
3. **Sequence**: The 16th sequence (Seq_Main_16th) is the heart - automate filter cutoff
4. **Sidechain**: Duck pads/atmospheres to kick
5. **Arrangement**: Use 16-bar Goa file for full journey, 8-bar for loops
6. **Transitions**: FX_Riser/Downer/Impact mark 4/8/16 bar boundaries

## License

MIT - Free for commercial and personal use.