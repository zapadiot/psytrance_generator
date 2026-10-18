#!/usr/bin/env python3
"""
Ollama Musician-Llama integration for psytrance generation.
Uses the local ollama model to generate MIDI token patterns.
"""

import json
import subprocess
import random
import time
from pathlib import Path
from typing import List, Tuple, Optional
import symusic

# Ollama configuration
OLLAMA_URL = "http://69.57.210.224:11434"
MODEL_NAME = "hf.co/mradermacher/Musician-Llama-3.2-1B-Instruct-GGUF:Q4_K_M"

# Psytrance-specific prompts for the model
PSYTRANCE_PROMPTS = {
    "kick_bass": """Generate a psytrance kick and bass pattern in 4/4 at 145 BPM. 
    Kick on every beat (1, 2, 3, 4). Rolling bassline 16th notes on root note A (57) and fifth E (64). 
    Output as MIDI tokens: time velocity pitch duration. 8 bars.""",
    
    "percussion": """Generate psytrance percussion pattern at 145 BPM. 
    Closed hi-hats 16th notes, open hats on 2 and 4, snare on 2 and 4, claps layered.
    Shakers and tambourines. 8 bars. Output MIDI tokens.""",
    
    "lead_sequence": """Generate psytrance lead and sequence at 145 BPM. 
    Driving 16th note sequence in A minor/Phrygian. Hypnotic lead melody. Acid 303 line.
    8 bars. Output MIDI tokens.""",
    
    "pads_atmosphere": """Generate psytrance pads and atmospheres at 145 BPM. 
    Evolving chord pads, space atmospheres, risers every 4 bars. 
    8 bars. Output MIDI tokens.""",
    
    "full_arrangement": """Generate a complete psytrance track at 145 BPM, 8 bars.
    Kick, bass, percussion, leads, sequences, pads, FX. 
    Psytrance style with rolling bass and driving sequences.
    Output as MIDI token format: time velocity pitch duration channel.""",
}


def query_ollama(prompt: str, temperature: float = 0.4, max_tokens: int = 4096) -> str:
    """Query the ollama model and return response."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", f"{OLLAMA_URL}/api/generate",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "model": MODEL_NAME,
                 "prompt": prompt,
                 "stream": False,
                 "options": {
                     "temperature": temperature,
                     "num_predict": max_tokens,
                     "top_p": 0.9,
                     "repeat_penalty": 1.1
                 }
             })],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("response", "")
        else:
            return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Timeout"
    except Exception as e:
        return f"Error: {e}"


def parse_midi_tokens(token_string: str) -> List[Tuple[int, int, int, int, int]]:
    """
    Parse MIDI token string into note events.
    Expected format: time velocity pitch duration [channel]
    Separated by periods or newlines.
    """
    notes = []
    # Split by periods, newlines, or semicolons
    import re
    segments = re.split(r'[.;\n]', token_string)
    
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        parts = segment.split()
        if len(parts) >= 4:
            try:
                time_val = int(parts[0])
                velocity = int(parts[1])
                pitch = int(parts[2])
                duration = int(parts[3])
                channel = int(parts[4]) if len(parts) > 4 else 0
                notes.append((time_val, velocity, pitch, duration, channel))
            except ValueError:
                continue
    return notes


def tokens_to_midi(notes: List[Tuple], output_path: Path, tpq: int = 480, scale_factor: float = 1.0):
    """Convert parsed tokens to MIDI file."""
    if not notes:
        return False
    
    score = symusic.Score()
    score.ticks_per_quarter = tpq
    
    # Group by channel
    channels = {}
    for time_val, velocity, pitch, duration, channel in notes:
        if channel not in channels:
            track = symusic.Track()
            track.program = 0
            track.is_drum = (channel == 9)  # Channel 10 = drums
            channels[channel] = track
        
        track = channels[channel]
        
        # Scale time and duration
        tick_time = int(time_val * scale_factor)
        dur_ticks = max(1, int(duration * scale_factor))
        
        # Clamp values
        pitch = max(0, min(127, pitch))
        velocity = max(1, min(127, velocity))
        
        note = symusic.Note(
            time=tick_time,
            duration=dur_ticks,
            pitch=pitch,
            velocity=velocity
        )
        track.notes.append(note)
    
    # Add tracks to score
    for channel, track in channels.items():
        track.name = f"Channel_{channel}"
        score.tracks.append(track)
    
    score.dump_midi(str(output_path))
    return True


def generate_with_ollama(category: str, output_dir: Path, bars: int = 8, 
                         bpm: int = 145, seed: int = None) -> Optional[Path]:
    """Generate a specific category using ollama."""
    if seed is not None:
        random.seed(seed)
    
    prompt = PSYTRANCE_PROMPTS.get(category, PSYTRANCE_PROMPTS["full_arrangement"])
    prompt = prompt.replace("145 BPM", f"{bpm} BPM").replace("8 bars", f"{bars} bars")
    
    print(f"  Querying ollama for {category}...")
    response = query_ollama(prompt)
    
    # Save raw response
    raw_path = output_dir / f"ollama_{category}_raw.txt"
    raw_path.write_text(response)
    
    # Parse tokens
    notes = parse_midi_tokens(response)
    print(f"    Parsed {len(notes)} notes")
    
    if not notes:
        print(f"    No valid tokens found")
        return None
    
    # Convert to MIDI
    # Model outputs seem to use small time values, scale to bars
    max_time = max(n[0] for n in notes) if notes else 1
    target_ticks = bars * 4 * 480  # bars * beats_per_bar * tpq
    scale_factor = target_ticks / max(max_time, 1)
    
    output_path = output_dir / f"ollama_{category}.mid"
    tokens_to_midi(notes, output_path, scale_factor=scale_factor)
    print(f"    Saved: {output_path}")
    
    return output_path


def generate_all_categories_ollama(output_dir: Path, bars: int = 8, 
                                   bpm: int = 145, seed: int = None) -> List[Path]:
    """Generate all categories using ollama."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    categories = ["kick_bass", "percussion", "lead_sequence", "pads_atmosphere"]
    results = []
    
    for cat in categories:
        path = generate_with_ollama(cat, output_dir, bars, bpm, seed)
        if path:
            results.append(path)
    
    # Also try full arrangement
    path = generate_with_ollama("full_arrangement", output_dir, bars, bpm, seed)
    if path:
        results.append(path)
    
    return results


def merge_ollama_with_algorithmic(ollama_dir: Path, algorithmic_score: symusic.Score, 
                                   output_path: Path) -> symusic.Score:
    """Merge ollama-generated tracks with algorithmic score."""
    # Load all ollama MIDI files
    ollama_tracks = []
    for mid_file in ollama_dir.glob("ollama_*.mid"):
        try:
            score = symusic.Score(str(mid_file))
            for track in score.tracks:
                track.name = f"Ollama_{mid_file.stem}_{track.name}"
                ollama_tracks.append(track)
        except Exception as e:
            print(f"  Could not load {mid_file}: {e}")
    
    # Create merged score
    merged = symusic.Score()
    merged.ticks_per_quarter = algorithmic_score.ticks_per_quarter
    
    # Add algorithmic tracks first
    for track in algorithmic_score.tracks:
        merged.tracks.append(track)
    
    # Add ollama tracks
    for track in ollama_tracks:
        merged.tracks.append(track)
    
    merged.dump_midi(str(output_path))
    print(f"  Merged score saved: {output_path} ({len(merged.tracks)} tracks)")
    
    return merged


if __name__ == "__main__":
    # Test generation
    output_dir = Path("/home/baboon/psytrance-generator/midi/ollama")
    generate_all_categories_ollama(output_dir, bars=4, bpm=145, seed=42)