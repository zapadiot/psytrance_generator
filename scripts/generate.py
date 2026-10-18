#!/usr/bin/env python3
"""
Quick psytrance MIDI generator - command line interface.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from psytrance_generator import generate_psytrance_midi, PsyConfig, ROOT_NOTES


def main():
    parser = argparse.ArgumentParser(description="Generate Psytrance/Goa MIDI")
    parser.add_argument("-o", "--output", default="psytrance_custom.mid", help="Output MIDI file")
    parser.add_argument("--bpm", type=int, default=145, help="BPM (default: 145)")
    parser.add_argument("--bars", type=int, default=8, help="Number of bars (default: 8)")
    parser.add_argument("--root", default="A", choices=list(ROOT_NOTES.keys()), help="Root note (default: A)")
    parser.add_argument("--scale", default="double_harmonic", 
                       choices=["minor", "phrygian", "harmonic_minor", "double_harmonic", "minor_pentatonic"],
                       help="Scale (default: double_harmonic)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    
    args = parser.parse_args()
    
    config = PsyConfig(bpm=args.bpm, bars=args.bars)
    output_path = Path(args.output)
    
    print(f"Generating: {output_path}")
    print(f"  BPM: {args.bpm}, Bars: {args.bars}, Root: {args.root}, Scale: {args.scale}")
    
    generate_psytrance_midi(output_path, config, args.root, args.scale, args.seed)
    print(f"Done!")


if __name__ == "__main__":
    main()