#!/usr/bin/env python3
"""
Unified Psytrance Generator - Creates full arrangement + stems + channels + ollama integration.
Outputs organized in subfolders:
- midi/full/        - Complete 47-track arrangements
- midi/stems/       - 5 stem groups (Kick, Bass, Perc, Leads, Pads_FX)
- midi/channels/    - Per-channel MIDI (16 files, one per MIDI channel)
- midi/ollama/      - Ollama model generated patterns
"""

import sys
import argparse
import random
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from psytrance_generator import (
    generate_psytrance_midi, PsyConfig, ROOT_NOTES, TRACK_SPECS, GM
)
import symusic


def save_per_channel(score: symusic.Score, output_dir: Path, prefix: str = ""):
    """Save each MIDI channel as separate file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Group tracks by channel (we'll assign channels programmatically)
    # Since symusic doesn't store channel on track, we assign based on track order/type
    channel_map = {}
    
    # Assign channels based on track categories
    for track in score.tracks:
        # Determine channel from track name/program
        name = track.name
        is_drum = track.is_drum
        
        if is_drum:
            channel = 9  # Channel 10 (0-indexed)
        elif 'Bass' in name:
            channel = 0
        elif any(x in name for x in ['Lead', 'Seq', 'Acid']):
            channel = 1
        elif any(x in name for x in ['Pad', 'Atmo', 'FX', 'Vocal', 'Glitch']):
            channel = 2
        else:
            channel = 3
        
        if channel not in channel_map:
            channel_map[channel] = []
        channel_map[channel].append(track)
    
    # Save each channel
    for ch, tracks in channel_map.items():
        ch_score = symusic.Score()
        ch_score.ticks_per_quarter = score.ticks_per_quarter
        for t in tracks:
            ch_score.tracks.append(t)
        
        ch_file = output_dir / f"{prefix}channel_{ch+1:02d}.mid"
        ch_score.dump_midi(str(ch_file))
        print(f"  Channel {ch+1}: {len(tracks)} tracks -> {ch_file.name}")


def save_stems(score: symusic.Score, output_dir: Path, prefix: str = ""):
    """Save stem groups."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    stem_groups = {
        "Kick": ["Kick_Main", "Kick_Sub", "Kick_Click"],
        "Bass": ["Bass_Sub", "Bass_Main", "Bass_FM", "Bass_Mid", "Bass_High", "Bass_Reso"],
        "Percussion": ["HH_Closed_Main", "HH_Closed_Ghost", "HH_Open", "HH_Ride",
                       "Snare_Main", "Snare_Ghost", "Clap_Main", "Clap_Layer",
                       "Perc_Shaker", "Perc_Tambourine", "Perc_Conga_Low", "Perc_Conga_High",
                       "Perc_Timbale", "Perc_Bongo", "Crash_Main", "Crash_FX"],
        "Leads": ["Lead_Main", "Lead_Layer", "Lead_Octave", "Lead_Reso",
                  "Seq_Main_16th", "Seq_Main_8th", "Seq_Counter", "Seq_Arp",
                  "Seq_Pluck", "Acid_Line"],
        "Pads_FX": ["Pad_Main", "Pad_Warm", "Pad_Evolve", "Pad_Dark",
                    "Atmo_Space", "Atmo_SciFi", "Atmo_Voice",
                    "FX_Riser", "FX_Downer", "FX_Impact",
                    "Vocal_Chop", "Glitch_Perc"],
    }
    
    for stem_name, track_names in stem_groups.items():
        stem_score = symusic.Score()
        stem_score.ticks_per_quarter = score.ticks_per_quarter
        
        for track in score.tracks:
            if track.name in track_names:
                stem_score.tracks.append(track)
        
        stem_file = output_dir / f"{prefix}STEMS_{stem_name}.mid"
        stem_score.dump_midi(str(stem_file))
        total_notes = sum(len(t.notes) for t in stem_score.tracks)
        print(f"  STEMS_{stem_name}: {len(stem_score.tracks)} tracks, {total_notes} notes -> {stem_file.name}")


def generate_all_variations(base_dir: Path, use_ollama: bool = False):
    """Generate all standard variations."""
    variations = [
        ("psytrance_145bpm_A_8bar", PsyConfig(bpm=145, bars=8), 'A', 'double_harmonic'),
        ("psytrance_148bpm_E_8bar", PsyConfig(bpm=148, bars=8), 'E', 'phrygian'),
        ("psytrance_150bpm_F#_4bar", PsyConfig(bpm=150, bars=4), 'F#', 'harmonic_minor'),
        ("goa_140bpm_A_16bar", PsyConfig(bpm=140, bars=16), 'A', 'double_harmonic'),
        ("darkpsy_152bpm_D_8bar", PsyConfig(bpm=152, bars=8), 'D', 'harmonic_minor'),
        ("prog_138bpm_G_8bar", PsyConfig(bpm=138, bars=8), 'G', 'minor'),
    ]
    
    for name, config, root, scale in variations:
        print(f"\n{'='*60}")
        print(f"Generating: {name}")
        
        # Full arrangement
        full_dir = base_dir / "full"
        full_path = full_dir / f"{name}.mid"
        score = generate_psytrance_midi(full_path, config, root, scale)
        
        # Stems
        stems_dir = base_dir / "stems"
        save_stems(score, stems_dir, prefix=f"{name}_")
        
        # Per-channel
        channels_dir = base_dir / "channels"
        save_per_channel(score, channels_dir, prefix=f"{name}_")
        
        print(f"  ✓ Complete: {name}")
    
    # Generate ollama patterns if requested
    if use_ollama:
        print(f"\n{'='*60}")
        print("Generating Ollama patterns...")
        ollama_dir = base_dir / "ollama"
        try:
            from ollama_integration import generate_all_categories_ollama
            generate_all_categories_ollama(ollama_dir, bars=8, bpm=145, seed=42)
            print("  ✓ Ollama patterns generated")
        except Exception as e:
            print(f"  Ollama generation failed: {e}")


def generate_custom(base_dir: Path, config: PsyConfig, root: str, scale: str, 
                    seed: int, name: str, use_ollama: bool = False):
    """Generate a single custom variation."""
    print(f"\n{'='*60}")
    print(f"Generating custom: {name}")
    print(f"  BPM: {config.bpm}, Bars: {config.bars}, Root: {root}, Scale: {scale}, Seed: {seed}")
    
    # Full arrangement
    full_dir = base_dir / "full"
    full_path = full_dir / f"{name}.mid"
    score = generate_psytrance_midi(full_path, config, root, scale, seed)
    
    # Stems
    stems_dir = base_dir / "stems"
    save_stems(score, stems_dir, prefix=f"{name}_")
    
    # Per-channel
    channels_dir = base_dir / "channels"
    save_per_channel(score, channels_dir, prefix=f"{name}_")
    
    print(f"  ✓ Complete: {name}")
    
    # Ollama
    if use_ollama:
        ollama_dir = base_dir / "ollama"
        try:
            from ollama_integration import generate_all_categories_ollama
            generate_all_categories_ollama(ollama_dir, bars=config.bars, bpm=config.bpm, seed=seed)
        except Exception as e:
            print(f"  Ollama failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Psytrance MIDI Generator - Full Output")
    parser.add_argument("--bpm", type=int, default=145, help="BPM")
    parser.add_argument("--bars", type=int, default=8, help="Number of bars")
    parser.add_argument("--root", default="A", choices=list(ROOT_NOTES.keys()), help="Root note")
    parser.add_argument("--scale", default="double_harmonic", 
                       choices=["minor", "phrygian", "harmonic_minor", "double_harmonic", "minor_pentonic"],
                       help="Scale")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (None = random)")
    parser.add_argument("--name", default=None, help="Custom name for output")
    parser.add_argument("--all", action="store_true", help="Generate all standard variations")
    parser.add_argument("--ollama", action="store_true", help="Also generate with ollama model")
    parser.add_argument("--output-dir", default="/home/baboon/psytrance-generator/midi", help="Output directory")
    
    args = parser.parse_args()
    
    # Set seed
    if args.seed is None:
        seed = int(time.time() * 1000) % 2**32
    else:
        seed = args.seed
    random.seed(seed)
    
    base_dir = Path(args.output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    if args.all:
        generate_all_variations(base_dir, use_ollama=args.ollama)
    else:
        config = PsyConfig(bpm=args.bpm, bars=args.bars)
        name = args.name or f"custom_{args.bpm}bpm_{args.root}_{args.scale}_{args.bars}bar_seed{seed}"
        generate_custom(base_dir, config, args.root, args.scale, seed, name, use_ollama=args.ollama)
    
    print(f"\n✅ All outputs in: {base_dir}")
    print(f"  full/     - Complete arrangements")
    print(f"  stems/    - 5 stem groups per variation")
    print(f"  channels/ - Per-channel MIDI per variation")
    if args.ollama:
        print(f"  ollama/   - Ollama model patterns")


if __name__ == "__main__":
    main()