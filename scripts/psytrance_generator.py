#!/usr/bin/env python3
"""
Psytrance / Goa Trance MIDI Generator
Generates a full 4-8 bar loop with 45+ tracks/layers across multiple instrument categories.

MIDI Channel Mapping (16 channels, multiple tracks per channel for DAW routing):
- Ch 1-4: Kick & Bass layers
- Ch 5-8: Percussion
- Ch 9-12: Leads & Sequences  
- Ch 13-16: Pads, FX, Atmospheres

Track count: ~50 tracks for full production setup
"""

import symusic
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum

# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class PsyConfig:
    bpm: int = 145
    bars: int = 8
    tpq: int = 480  # ticks per quarter
    swing: float = 0.0  # psytrance is straight
    
    @property
    def beat_ticks(self) -> int:
        return self.tpq
    
    @property
    def bar_ticks(self) -> int:
        return 4 * self.beat_ticks
    
    @property
    def sixteenth(self) -> int:
        return self.tpq // 4
    
    @property
    def total_ticks(self) -> int:
        return self.bars * self.bar_ticks


class GM(Enum):
    """General MIDI drum map + synth patches"""
    # Drums (Channel 10)
    KICK = 35
    SNARE = 38
    CLAP = 39
    CLOSED_HH = 42
    OPEN_HH = 46
    RIDE = 51
    CRASH = 49
    SHAKER = 70
    TAMBOURINE = 54
    CONGA_LOW = 64
    CONGA_HIGH = 63
    TIMPANI = 47
    
    # Synth patches (for melodic channels)
    SAW_LEAD = 81
    SQUARE_LEAD = 80
    CALLIOPE = 82
    CHIFF_LEAD = 83
    CHARANG = 84
    VOICE_LEAD = 85
    FIFTHS_LEAD = 86
    BASS_LEAD = 87
    POLYSYNTH = 90
    SPACE_VOICE = 91
    BOWED_GLASS = 92
    METAL_PAD = 93
    HALO_PAD = 94
    SWEEP_PAD = 95
    FX_RAIN = 96
    FX_SOUNDTRACK = 97
    FX_CRYSTAL = 98
    FX_ATMOSPHERE = 99
    FX_BRIGHTNESS = 100
    FX_GOBLINS = 101
    FX_ECHOES = 102
    FX_SCI_FI = 103


# Psytrance musical scales
SCALES = {
    'minor': [0, 2, 3, 5, 7, 8, 10],  # Natural minor
    'phrygian': [0, 1, 3, 5, 7, 8, 10],  # Phrygian (dark)
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],  # Harmonic minor
    'double_harmonic': [0, 1, 4, 5, 7, 8, 11],  # Byzantine (very Goa)
    'minor_pentatonic': [0, 3, 5, 7, 10],
}

ROOT_NOTES = {
    'A': 57, 'A#': 58, 'Bb': 58, 'B': 59, 'C': 60, 'C#': 61, 'Db': 61,
    'D': 62, 'D#': 63, 'Eb': 63, 'E': 64, 'F': 65, 'F#': 66, 'Gb': 66,
    'G': 67, 'G#': 68, 'Ab': 68
}


# ============================================================
# TRACK DEFINITIONS
# ============================================================

@dataclass
class TrackSpec:
    name: str
    channel: int  # 0-15
    program: int  # GM patch
    is_drum: bool = False
    port: int = 0  # For multi-port routing (0-2)


# 45+ Track specifications for full psytrance production
TRACK_SPECS = [
    # ===== KICK & BASS (Channels 0-3) =====
    TrackSpec("Kick_Main", 0, 0, is_drum=True),
    TrackSpec("Kick_Sub", 0, 0, is_drum=True),
    TrackSpec("Kick_Click", 0, 0, is_drum=True),
    TrackSpec("Bass_Sub", 1, GM.BASS_LEAD.value),
    TrackSpec("Bass_Main", 1, GM.BASS_LEAD.value),
    TrackSpec("Bass_FM", 2, GM.SQUARE_LEAD.value),
    TrackSpec("Bass_Mid", 2, GM.SAW_LEAD.value),
    TrackSpec("Bass_High", 3, GM.CHIFF_LEAD.value),
    TrackSpec("Bass_Reso", 3, GM.CALLIOPE.value),
    
    # ===== PERCUSSION (Channels 4-7) =====
    TrackSpec("HH_Closed_Main", 4, 0, is_drum=True),
    TrackSpec("HH_Closed_Ghost", 4, 0, is_drum=True),
    TrackSpec("HH_Open", 4, 0, is_drum=True),
    TrackSpec("HH_Ride", 5, 0, is_drum=True),
    TrackSpec("Snare_Main", 5, 0, is_drum=True),
    TrackSpec("Snare_Ghost", 5, 0, is_drum=True),
    TrackSpec("Clap_Main", 6, 0, is_drum=True),
    TrackSpec("Clap_Layer", 6, 0, is_drum=True),
    TrackSpec("Perc_Shaker", 6, 0, is_drum=True),
    TrackSpec("Perc_Tambourine", 7, 0, is_drum=True),
    TrackSpec("Perc_Conga_Low", 7, 0, is_drum=True),
    TrackSpec("Perc_Conga_High", 7, 0, is_drum=True),
    TrackSpec("Perc_Timbale", 7, 0, is_drum=True),
    TrackSpec("Perc_Bongo", 7, 0, is_drum=True),
    TrackSpec("Crash_Main", 7, 0, is_drum=True),
    TrackSpec("Crash_FX", 7, 0, is_drum=True),
    
    # ===== LEADS & SEQUENCES (Channels 8-11) =====
    TrackSpec("Lead_Main", 8, GM.SAW_LEAD.value),
    TrackSpec("Lead_Layer", 8, GM.SQUARE_LEAD.value),
    TrackSpec("Lead_Octave", 9, GM.CALLIOPE.value),
    TrackSpec("Lead_Reso", 9, GM.CHIFF_LEAD.value),
    TrackSpec("Seq_Main_16th", 10, GM.POLYSYNTH.value),
    TrackSpec("Seq_Main_8th", 10, GM.SAW_LEAD.value),
    TrackSpec("Seq_Counter", 11, GM.FIFTHS_LEAD.value),
    TrackSpec("Seq_Arp", 11, GM.CALLIOPE.value),
    TrackSpec("Seq_Pluck", 11, GM.CHIFF_LEAD.value),
    TrackSpec("Acid_Line", 11, GM.SQUARE_LEAD.value),
    
    # ===== PADS & ATMOSPHERES (Channels 12-15) =====
    TrackSpec("Pad_Main", 12, GM.POLYSYNTH.value),
    TrackSpec("Pad_Warm", 12, GM.HALO_PAD.value),
    TrackSpec("Pad_Evolve", 13, GM.SWEEP_PAD.value),
    TrackSpec("Pad_Dark", 13, GM.METAL_PAD.value),
    TrackSpec("Atmo_Space", 14, GM.FX_ATMOSPHERE.value),
    TrackSpec("Atmo_SciFi", 14, GM.FX_SCI_FI.value),
    TrackSpec("Atmo_Voice", 15, GM.SPACE_VOICE.value),
    TrackSpec("FX_Riser", 15, GM.FX_BRIGHTNESS.value),
    TrackSpec("FX_Downer", 15, GM.FX_ECHOES.value),
    TrackSpec("FX_Impact", 15, GM.FX_GOBLINS.value),
    TrackSpec("Vocal_Chop", 15, GM.VOICE_LEAD.value),
    TrackSpec("Glitch_Perc", 15, GM.FX_CRYSTAL.value),
]


# ============================================================
# PATTERN GENERATORS
# ============================================================

class PsyPatternGenerator:
    def __init__(self, config: PsyConfig, root: int = 57, scale_name: str = 'double_harmonic', seed: int = None):
        self.cfg = config
        self.root = root
        self.scale = SCALES[scale_name]
        self.rng = random.Random(seed)  # Use passed seed
        
    def scale_note(self, degree: int, octave: int = 0) -> int:
        """Get MIDI note from scale degree and octave."""
        scale_len = len(self.scale)
        note_idx = degree % scale_len
        oct = degree // scale_len + octave
        return self.root + self.scale[note_idx] + oct * 12
    
    def add_note(self, track: symusic.Track, time: int, pitch: int, 
                 dur: int, vel: int, channel: int = None):
        """Add note to track."""
        note = symusic.Note(
            time=time,
            duration=dur,
            pitch=pitch,
            velocity=min(127, max(1, vel))
        )
        track.notes.append(note)
    
    # ----- KICK PATTERNS -----
    def gen_kick_main(self, track: symusic.Track):
        """Main kick - four on floor with psytrance accent."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for beat in range(4):
                time = bar_start + beat * self.cfg.beat_ticks
                # Accent on 1 and 3
                vel = 127 if beat in [0, 2] else 110
                # Psytrance kick: longer decay
                dur = self.cfg.beat_ticks // 2
                self.add_note(track, time, GM.KICK.value, dur, vel)
    
    def gen_kick_sub(self, track: symusic.Track):
        """Sub kick - deeper, less click."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for beat in range(4):
                time = bar_start + beat * self.cfg.beat_ticks
                # Slightly delayed for layering
                time += self.cfg.tpq // 192  # ~2.5ms
                vel = 100 if beat in [0, 2] else 85
                dur = self.cfg.beat_ticks * 3 // 4
                self.add_note(track, time, GM.KICK.value, dur, vel)
    
    def gen_kick_click(self, track: symusic.Track):
        """Click layer for attack."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for beat in range(4):
                time = bar_start + beat * self.cfg.beat_ticks
                vel = 90
                dur = self.cfg.tpq // 48  # Very short click
                self.add_note(track, time, GM.KICK.value, dur, vel)
    
    # ----- BASS PATTERNS (The heart of psytrance) -----
    def gen_bass_sub(self, track: symusic.Track):
        """Sub bass - root note, long sustain."""
        root_note = self.root - 12  # Sub octave
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            # Whole note per bar (with slight gap)
            time = bar_start
            dur = self.cfg.bar_ticks - self.cfg.sixteenth
            vel = 100
            self.add_note(track, time, root_note, dur, vel)
    
    def gen_bass_main(self, track: symusic.Track):
        """Main rolling bass - 16th notes with pattern."""
        # Classic psytrance bass pattern (in 16ths)
        # 1: root, 2: root, 3: root, 4: 5th, 5: root, 6: root, 7: octave, 8: 5th...
        pattern_16th = [
            0, 0, 0, 4,   # Bar 1: root root root 5th
            0, 0, 7, 4,   # Bar 2: root root octave 5th
            0, 3, 0, 4,   # Bar 3: root minor3rd root 5th
            0, 0, 7, 10,  # Bar 4: root root octave minor7th
        ]
        
        note_idx = 0
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for sixteenth in range(16):
                time = bar_start + sixteenth * self.cfg.sixteenth
                degree = pattern_16th[note_idx % len(pattern_16th)]
                pitch = self.scale_note(degree, -1)  # Bass octave
                
                # Velocity variation (psytrance groove)
                base_vel = 110
                if sixteenth % 4 == 0:
                    vel = base_vel + 10  # Downbeat accent
                elif sixteenth % 4 == 2:
                    vel = base_vel + 5   # Offbeat
                else:
                    vel = base_vel - 5
                vel += self.rng.randint(-3, 3)
                
                # Duration: legato 16ths with tiny gap
                dur = self.cfg.sixteenth - self.cfg.tpq // 192
                
                self.add_note(track, time, pitch, dur, min(127, max(1, vel)))
                note_idx += 1
    
    def gen_bass_fm(self, track: symusic.Track):
        """FM bass layer - metallic timbre, different pattern."""
        pattern = [0, -1, 0, 3, 0, -1, 0, 4] * 2  # 16 steps
        
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for i, degree in enumerate(pattern):
                time = bar_start + i * self.cfg.sixteenth * 2  # 8th notes
                pitch = self.scale_note(degree, -1)
                vel = 70 + self.rng.randint(-5, 5)
                dur = self.cfg.sixteenth * 2 - self.cfg.tpq // 96
                self.add_note(track, time, pitch, dur, vel)
    
    def gen_bass_mid(self, track: symusic.Track):
        """Mid bass - harmonic content."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            # Play on offbeats (2&, 4&)
            for beat_off in [1.5, 3.5]:
                time = int(bar_start + beat_off * self.cfg.beat_ticks)
                pitch = self.scale_note(7, -1)  # Octave
                vel = 60
                dur = self.cfg.sixteenth
                self.add_note(track, time, pitch, dur, vel)
    
    def gen_bass_high(self, track: symusic.Track):
        """High bass - harmonic sparkle."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            # Every 3rd 16th (polyrhythm feel)
            for i in range(0, 16, 3):
                time = bar_start + i * self.cfg.sixteenth
                pitch = self.scale_note(12, -1)  # Octave + 5th
                vel = 50
                dur = self.cfg.sixteenth // 2
                self.add_note(track, time, pitch, dur, vel)
    
    def gen_bass_reso(self, track: symusic.Track):
        """Resonant bass accent - filter sweep moments."""
        for bar in range(self.cfg.bars):
            if bar % 2 == 1:  # Every other bar
                bar_start = bar * self.cfg.bar_ticks
                # End of bar fill
                time = bar_start + self.cfg.bar_ticks - self.cfg.sixteenth * 2
                pitch = self.scale_note(0, 0)  # Root at normal octave
                vel = 80
                dur = self.cfg.sixteenth * 2
                self.add_note(track, time, pitch, dur, vel)
    
    # ----- PERCUSSION -----
    def gen_hh_closed_main(self, track: symusic.Track):
        """Main closed hi-hat - 16th notes."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for i in range(16):
                time = bar_start + i * self.cfg.sixteenth
                # Accent pattern
                if i % 4 == 0:
                    vel = 100
                elif i % 4 == 2:
                    vel = 85
                else:
                    vel = 70
                vel += self.rng.randint(-5, 5)
                dur = self.cfg.sixteenth // 2
                self.add_note(track, time, GM.CLOSED_HH.value, dur, vel)
    
    def gen_hh_closed_ghost(self, track: symusic.Track):
        """Ghost hi-hats - 32nd notes on offbeats."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for i in range(16):
                if i % 2 == 1:  # Off 16ths
                    time = bar_start + i * self.cfg.sixteenth + self.cfg.sixteenth // 2
                    vel = 35 + self.rng.randint(-5, 5)
                    dur = self.cfg.sixteenth // 4
                    self.add_note(track, time, GM.CLOSED_HH.value, dur, vel)
    
    def gen_hh_open(self, track: symusic.Track):
        """Open hi-hats - on 2 and 4 (and variations)."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            # Standard on 2 and 4
            for beat in [1, 3]:
                time = bar_start + beat * self.cfg.beat_ticks
                vel = 90
                dur = self.cfg.beat_ticks // 2
                self.add_note(track, time, GM.OPEN_HH.value, dur, vel)
            # Extra on 4& every 2 bars
            if bar % 2 == 1:
                time = bar_start + 3 * self.cfg.beat_ticks + self.cfg.sixteenth * 2
                vel = 70
                dur = self.cfg.sixteenth
                self.add_note(track, time, GM.OPEN_HH.value, dur, vel)
    
    def gen_hh_ride(self, track: symusic.Track):
        """Ride pattern - for groove sections."""
        for bar in range(self.cfg.bars):
            if bar >= self.cfg.bars // 2:  # Second half
                bar_start = bar * self.cfg.bar_ticks
                for beat in range(4):
                    time = bar_start + beat * self.cfg.beat_ticks
                    vel = 60
                    dur = self.cfg.sixteenth
                    self.add_note(track, time, GM.RIDE.value, dur, vel)
    
    def gen_snare_main(self, track: symusic.Track):
        """Main snare - on 2 and 4."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for beat in [1, 3]:
                time = bar_start + beat * self.cfg.beat_ticks
                vel = 110
                dur = self.cfg.sixteenth
                self.add_note(track, time, GM.SNARE.value, dur, vel)
    
    def gen_snare_ghost(self, track: symusic.Track):
        """Ghost snares - fills."""
        for bar in range(self.cfg.bars):
            if bar % 4 == 3:  # Every 4th bar
                bar_start = bar * self.cfg.bar_ticks
                # Fast rolls at end of bar
                for i in range(4):
                    time = bar_start + self.cfg.bar_ticks - (4-i) * self.cfg.sixteenth
                    vel = 50 - i * 5
                    dur = self.cfg.sixteenth // 2
                    self.add_note(track, time, GM.SNARE.value, dur, vel)
    
    def gen_clap_main(self, track: symusic.Track):
        """Main clap - layered with snare on 2 and 4."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for beat in [1, 3]:
                time = bar_start + beat * self.cfg.beat_ticks + self.cfg.tpq // 192  # Slight delay
                vel = 100
                dur = self.cfg.sixteenth
                self.add_note(track, time, GM.CLAP.value, dur, vel)
    
    def gen_clap_layer(self, track: symusic.Track):
        """Second clap layer - wider."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for beat in [1, 3]:
                time = bar_start + beat * self.cfg.beat_ticks + self.cfg.tpq // 96
                vel = 80
                dur = self.cfg.sixteenth * 2
                self.add_note(track, time, GM.CLAP.value, dur, vel)
    
    def gen_shaker(self, track: symusic.Track):
        """Shaker - 16th note groove."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for i in range(16):
                time = bar_start + i * self.cfg.sixteenth
                # Skip some for groove
                if self.rng.random() < 0.3:
                    continue
                vel = 40 + (i % 4) * 5 + self.rng.randint(-5, 5)
                dur = self.cfg.sixteenth // 3
                self.add_note(track, time, GM.SHAKER.value, dur, vel)
    
    def gen_tambourine(self, track: symusic.Track):
        """Tambourine - on 2 and 4, 16th pattern."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for beat in [1, 3]:
                for i in range(4):
                    time = bar_start + beat * self.cfg.beat_ticks + i * self.cfg.sixteenth
                    vel = 50 - i * 8
                    dur = self.cfg.sixteenth
                    self.add_note(track, time, GM.TAMBOURINE.value, dur, vel)
    
    def gen_congas(self, track: symusic.Track, pitch: int, density: float = 0.3):
        """Conga pattern."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for i in range(16):
                if self.rng.random() < density:
                    time = bar_start + i * self.cfg.sixteenth
                    vel = 60 + self.rng.randint(-10, 10)
                    dur = self.cfg.sixteenth
                    self.add_note(track, time, pitch, dur, vel)
    
    def gen_crash(self, track: symusic.Track, pitch: int, every_bars: int = 4):
        """Crash cymbals - section markers."""
        for bar in range(self.cfg.bars):
            if bar % every_bars == 0:
                bar_start = bar * self.cfg.bar_ticks
                time = bar_start
                vel = 100
                dur = self.cfg.beat_ticks
                self.add_note(track, time, pitch, dur, vel)
    
    # ----- LEADS & SEQUENCES -----
    def gen_lead_main(self, track: symusic.Track):
        """Main lead melody - hypnotic psytrance."""
        # Create a repeating melodic motif
        motif = [
            (0, 1.0), (2, 0.5), (3, 0.5), (5, 1.0),  # Bar 1
            (7, 1.0), (5, 0.5), (3, 0.5), (2, 1.0),  # Bar 2
            (0, 1.0), (1, 0.5), (3, 0.5), (5, 1.0),  # Bar 3 (phyrygian flavor)
            (7, 1.0), (8, 0.5), (10, 0.5), (7, 1.0), # Bar 4
        ]
        
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            motif_idx = bar % len(motif)
            degree, dur_beats = motif[motif_idx]
            pitch = self.scale_note(degree, 1)  # Lead octave
            time = bar_start
            dur = int(dur_beats * self.cfg.beat_ticks)
            vel = 95
            self.add_note(track, time, pitch, dur, vel)
    
    def gen_lead_layer(self, track: symusic.Track):
        """Lead layer - harmony/octave."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            # Play fifth above main lead
            pitch = self.scale_note(4, 1)  # Fifth
            time = bar_start + self.cfg.sixteenth  # Slight delay
            dur = self.cfg.beat_ticks * 3
            vel = 70
            self.add_note(track, time, pitch, dur, vel)
    
    def gen_seq_16th(self, track: symusic.Track):
        """Main 16th note sequence - the driving force."""
        # Classic psytrance sequence pattern
        seq_pattern = [
            0, 0, 3, 0, 5, 0, 3, 0,  7, 0, 5, 0, 3, 0, 2, 0  # 16 steps
        ]
        
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for i, degree in enumerate(seq_pattern):
                time = bar_start + i * self.cfg.sixteenth
                pitch = self.scale_note(degree, 1)
                
                # Velocity: accent every 4th, ghost others
                if i % 4 == 0:
                    vel = 100
                elif i % 2 == 0:
                    vel = 75
                else:
                    vel = 60
                vel += self.rng.randint(-5, 5)
                
                dur = self.cfg.sixteenth - self.cfg.tpq // 192
                self.add_note(track, time, pitch, dur, vel)
    
    def gen_seq_8th(self, track: symusic.Track):
        """8th note sequence - counter rhythm."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for i in range(8):
                time = bar_start + i * self.cfg.sixteenth * 2
                degree = [0, 7, 3, 7, 5, 7, 3, 7][i]
                pitch = self.scale_note(degree, 1)
                vel = 80
                dur = self.cfg.sixteenth * 2 - self.cfg.tpq // 96
                self.add_note(track, time, pitch, dur, vel)
    
    def gen_seq_counter(self, track: symusic.Track):
        """Counter sequence - offbeat."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            # Play on the "ands"
            for i in range(8):
                time = bar_start + i * self.cfg.sixteenth * 2 + self.cfg.sixteenth
                degree = [10, 8, 7, 5, 3, 2, 0, 1][i]  # Descending
                pitch = self.scale_note(degree, 1)
                vel = 65
                dur = self.cfg.sixteenth
                self.add_note(track, time, pitch, dur, vel)
    
    def gen_seq_arp(self, track: symusic.Track):
        """Arpeggiator - fast runs."""
        for bar in range(self.cfg.bars):
            if bar % 2 == 0:  # Every other bar
                bar_start = bar * self.cfg.bar_ticks
                # Fast 32nd note run
                for i in range(8):
                    time = bar_start + self.cfg.bar_ticks - 8 * self.cfg.sixteenth // 2 + i * self.cfg.sixteenth // 2
                    degree = i % 7
                    pitch = self.scale_note(degree, 2)
                    vel = 70 - i * 3
                    dur = self.cfg.sixteenth // 2
                    self.add_note(track, time, pitch, dur, vel)
    
    def gen_seq_pluck(self, track: symusic.Track):
        """Pluck sound - short stabs."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            # On beat 1 and 3&
            for offset in [0, 7]:
                time = bar_start + offset * self.cfg.sixteenth
                pitch = self.scale_note(0, 2)  # High root
                vel = 85
                dur = self.cfg.sixteenth // 2
                self.add_note(track, time, pitch, dur, vel)
    
    def gen_acid_line(self, track: symusic.Track):
        """Acid line - 303 style squelch."""
        # Simple acid pattern: root, octave, 5th, octave with slides
        acid_pattern = [0, 12, 7, 12, 0, 12, 5, 12]
        
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            for i, degree in enumerate(acid_pattern):
                time = bar_start + i * self.cfg.sixteenth * 2
                pitch = self.root + degree  # Direct semitone for acid
                vel = 90
                dur = self.cfg.sixteenth * 2 - self.cfg.tpq // 96
                self.add_note(track, time, pitch, dur, vel)
    
    # ----- PADS & ATMOSPHERES -----
    def gen_pad_main(self, track: symusic.Track):
        """Main pad - sustained chords."""
        # Chord progression: i - VI - III - VII (in minor)
        chords = [
            [0, 3, 7],      # i minor
            [5, 8, 12],     # VI major
            [3, 7, 10],     # III major
            [7, 10, 14],    # VII major
        ]
        
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            chord = chords[bar % len(chords)]
            for degree in chord:
                pitch = self.scale_note(degree, 0)  # Mid octave
                time = bar_start
                dur = self.cfg.bar_ticks - self.cfg.sixteenth
                vel = 55
                self.add_note(track, time, pitch, dur, vel)
    
    def gen_pad_evolve(self, track: symusic.Track):
        """Evolving pad - filter automation via velocity."""
        for bar in range(self.cfg.bars):
            bar_start = bar * self.cfg.bar_ticks
            # Add notes that swell
            for i, beat in enumerate([0, 1, 2, 3]):
                time = bar_start + beat * self.cfg.beat_ticks
                pitch = self.scale_note([0, 5, 3, 7][i], 0)
                vel = 40 + bar * 10  # Swells over 8 bars
                dur = self.cfg.beat_ticks * 2
                self.add_note(track, time, pitch, dur, min(127, vel))
    
    def gen_atmo_space(self, track: symusic.Track):
        """Space atmosphere - long notes."""
        for bar in range(0, self.cfg.bars, 4):
            bar_start = bar * self.cfg.bar_ticks
            pitch = self.root + 24  # High
            time = bar_start
            dur = 4 * self.cfg.bar_ticks
            vel = 45
            self.add_note(track, time, pitch, dur, vel)
    
    def gen_fx_riser(self, track: symusic.Track):
        """Riser - pitch bend up (simulated with ascending notes)."""
        for bar in range(self.cfg.bars):
            if bar % 4 == 3:  # Every 4th bar
                bar_start = bar * self.cfg.bar_ticks
                # Ascending 32nd notes over last 2 beats
                for i in range(16):
                    time = bar_start + self.cfg.bar_ticks * 2 + i * self.cfg.sixteenth // 2
                    pitch = self.root + 24 + i
                    vel = 50 + i * 3
                    dur = self.cfg.sixteenth // 2
                    self.add_note(track, time, pitch, dur, min(127, vel))
    
    def gen_fx_downer(self, track: symusic.Track):
        """Downer - opposite of riser."""
        for bar in range(self.cfg.bars):
            if bar % 4 == 0 and bar > 0:
                bar_start = bar * self.cfg.bar_ticks
                for i in range(8):
                    time = bar_start + i * self.cfg.sixteenth
                    pitch = self.root + 36 - i * 2
                    vel = 80 - i * 8
                    dur = self.cfg.sixteenth
                    self.add_note(track, time, pitch, dur, max(1, vel))
    
    def gen_fx_impact(self, track: symusic.Track):
        """Impact hits - on bar 1 of sections."""
        for bar in range(0, self.cfg.bars, 4):
            bar_start = bar * self.cfg.bar_ticks
            time = bar_start
            pitch = self.root - 12
            vel = 120
            dur = self.cfg.beat_ticks
            self.add_note(track, time, pitch, dur, vel)
    
    def gen_vocal_chop(self, track: symusic.Track):
        """Vocal chops - rhythmic."""
        for bar in range(self.cfg.bars):
            if bar % 2 == 1:
                bar_start = bar * self.cfg.bar_ticks
                # Chopped vocal on offbeats
                for i in [2, 6, 10, 14]:
                    time = bar_start + i * self.cfg.sixteenth
                    pitch = self.scale_note(self.rng.choice([0, 3, 7]), 1)
                    vel = 75
                    dur = self.cfg.sixteenth // 2
                    self.add_note(track, time, pitch, dur, vel)
    
    def gen_glitch_perc(self, track: symusic.Track):
        """Glitch percussion - random clicks."""
        for bar in range(self.cfg.bars):
            if self.rng.random() < 0.5:
                bar_start = bar * self.cfg.bar_ticks
                for _ in range(self.rng.randint(1, 4)):
                    time = bar_start + self.rng.randint(0, self.cfg.bar_ticks)
                    pitch = self.rng.choice([84, 88, 91, 96])  # High percussive
                    vel = self.rng.randint(40, 80)
                    dur = self.cfg.tpq // 96
                    self.add_note(track, time, pitch, dur, vel)


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_psytrance_midi(
    output_path: Path,
    config: PsyConfig = None,
    root_note: str = 'A',
    scale: str = 'double_harmonic',
    seed: int = 42
):
    """Generate complete psytrance MIDI arrangement."""
    
    if config is None:
        config = PsyConfig()
    
    random.seed(seed)
    root = ROOT_NOTES[root_note]
    
    print(f"Generating Psytrance/Goa MIDI:")
    print(f"  BPM: {config.bpm}")
    print(f"  Bars: {config.bars}")
    print(f"  Root: {root_note} ({root})")
    print(f"  Scale: {scale}")
    print(f"  Tracks: {len(TRACK_SPECS)}")
    
    gen = PsyPatternGenerator(config, root, scale, seed)
    
    # Create score
    score = symusic.Score()
    score.ticks_per_quarter = config.tpq
    
    # Track name to generator method mapping
    generators = {
        "Kick_Main": gen.gen_kick_main,
        "Kick_Sub": gen.gen_kick_sub,
        "Kick_Click": gen.gen_kick_click,
        "Bass_Sub": gen.gen_bass_sub,
        "Bass_Main": gen.gen_bass_main,
        "Bass_FM": gen.gen_bass_fm,
        "Bass_Mid": gen.gen_bass_mid,
        "Bass_High": gen.gen_bass_high,
        "Bass_Reso": gen.gen_bass_reso,
        "HH_Closed_Main": gen.gen_hh_closed_main,
        "HH_Closed_Ghost": gen.gen_hh_closed_ghost,
        "HH_Open": gen.gen_hh_open,
        "HH_Ride": gen.gen_hh_ride,
        "Snare_Main": gen.gen_snare_main,
        "Snare_Ghost": gen.gen_snare_ghost,
        "Clap_Main": gen.gen_clap_main,
        "Clap_Layer": gen.gen_clap_layer,
        "Perc_Shaker": gen.gen_shaker,
        "Perc_Tambourine": gen.gen_tambourine,
        "Perc_Conga_Low": lambda t: gen.gen_congas(t, GM.CONGA_LOW.value),
        "Perc_Conga_High": lambda t: gen.gen_congas(t, GM.CONGA_HIGH.value, 0.2),
        "Perc_Timbale": lambda t: gen.gen_congas(t, 65, 0.15),
        "Perc_Bongo": lambda t: gen.gen_congas(t, 60, 0.15),
        "Crash_Main": lambda t: gen.gen_crash(t, GM.CRASH.value, 4),
        "Crash_FX": lambda t: gen.gen_crash(t, GM.CRASH.value, 8),
        "Lead_Main": gen.gen_lead_main,
        "Lead_Layer": gen.gen_lead_layer,
        "Lead_Octave": gen.gen_lead_layer,
        "Lead_Reso": gen.gen_lead_layer,
        "Seq_Main_16th": gen.gen_seq_16th,
        "Seq_Main_8th": gen.gen_seq_8th,
        "Seq_Counter": gen.gen_seq_counter,
        "Seq_Arp": gen.gen_seq_arp,
        "Seq_Pluck": gen.gen_seq_pluck,
        "Acid_Line": gen.gen_acid_line,
        "Pad_Main": gen.gen_pad_main,
        "Pad_Warm": gen.gen_pad_main,
        "Pad_Evolve": gen.gen_pad_evolve,
        "Pad_Dark": gen.gen_pad_evolve,
        "Atmo_Space": gen.gen_atmo_space,
        "Atmo_SciFi": gen.gen_atmo_space,
        "Atmo_Voice": gen.gen_atmo_space,
        "FX_Riser": gen.gen_fx_riser,
        "FX_Downer": gen.gen_fx_downer,
        "FX_Impact": gen.gen_fx_impact,
        "Vocal_Chop": gen.gen_vocal_chop,
        "Glitch_Perc": gen.gen_glitch_perc,
    }
    
    # Create tracks
    for spec in TRACK_SPECS:
        track = symusic.Track()
        track.name = spec.name
        track.program = spec.program
        track.is_drum = spec.is_drum
        
        # Generate pattern
        if spec.name in generators:
            generators[spec.name](track)
        
        score.tracks.append(track)
        note_count = len(track.notes)
        print(f"  {spec.name:25s}: {note_count:4d} notes")
    
    # Save
    score.dump_midi(str(output_path))
    print(f"\nSaved: {output_path}")
    return score


# ============================================================
# VARIATIONS
# ============================================================

def generate_variations():
    """Generate multiple variations."""
    output_dir = Path("/home/baboon/psytrance-generator/midi")
    output_dir.mkdir(exist_ok=True)
    
    configs = [
        ("psytrance_145bpm_A_8bar", PsyConfig(bpm=145, bars=8), 'A', 'double_harmonic'),
        ("psytrance_148bpm_E_8bar", PsyConfig(bpm=148, bars=8), 'E', 'phrygian'),
        ("psytrance_150bpm_F#_4bar", PsyConfig(bpm=150, bars=4), 'F#', 'harmonic_minor'),
        ("goa_140bpm_A_16bar", PsyConfig(bpm=140, bars=16), 'A', 'double_harmonic'),
        ("darkpsy_152bpm_D_8bar", PsyConfig(bpm=152, bars=8), 'D', 'harmonic_minor'),
        ("prog_138bpm_G_8bar", PsyConfig(bpm=138, bars=8), 'G', 'minor'),
    ]
    
    for name, config, root, scale in configs:
        print(f"\n{'='*60}")
        print(f"Generating: {name}")
        output_path = output_dir / f"{name}.mid"
        generate_psytrance_midi(output_path, config, root, scale)
    
    # Also generate stem groups for mixing
    generate_stem_groups(output_dir, seed)


def generate_stem_groups(output_dir: Path, seed: int = None):
    """Generate grouped stems for mixing (Kick, Bass, Perc, Leads, FX)."""
    print(f"\n{'='*60}")
    print("Generating stem groups...")
    
    config = PsyConfig(bpm=145, bars=8)
    root = ROOT_NOTES['A']
    gen = PsyPatternGenerator(config, root, 'double_harmonic', seed)
    
    stem_groups = {
        "STEMS_Kick": [
            ("Kick_Main", 0, 0, True),
            ("Kick_Sub", 0, 0, True),
            ("Kick_Click", 0, 0, True),
        ],
        "STEMS_Bass": [
            ("Bass_Sub", 1, GM.BASS_LEAD.value, False),
            ("Bass_Main", 1, GM.BASS_LEAD.value, False),
            ("Bass_FM", 2, GM.SQUARE_LEAD.value, False),
            ("Bass_Mid", 2, GM.SAW_LEAD.value, False),
            ("Bass_High", 3, GM.CHIFF_LEAD.value, False),
            ("Bass_Reso", 3, GM.CALLIOPE.value, False),
        ],
        "STEMS_Percussion": [
            ("HH_Closed_Main", 4, 0, True),
            ("HH_Closed_Ghost", 4, 0, True),
            ("HH_Open", 4, 0, True),
            ("HH_Ride", 5, 0, True),
            ("Snare_Main", 5, 0, True),
            ("Snare_Ghost", 5, 0, True),
            ("Clap_Main", 6, 0, True),
            ("Clap_Layer", 6, 0, True),
            ("Perc_Shaker", 6, 0, True),
            ("Perc_Tambourine", 7, 0, True),
            ("Perc_Conga_Low", 7, 0, True),
            ("Perc_Conga_High", 7, 0, True),
            ("Crash_Main", 7, 0, True),
            ("Crash_FX", 7, 0, True),
        ],
        "STEMS_Leads": [
            ("Lead_Main", 8, GM.SAW_LEAD.value, False),
            ("Lead_Layer", 8, GM.SQUARE_LEAD.value, False),
            ("Seq_Main_16th", 9, GM.POLYSYNTH.value, False),
            ("Seq_Main_8th", 9, GM.SAW_LEAD.value, False),
            ("Seq_Counter", 10, GM.FIFTHS_LEAD.value, False),
            ("Seq_Arp", 10, GM.CALLIOPE.value, False),
            ("Seq_Pluck", 11, GM.CHIFF_LEAD.value, False),
            ("Acid_Line", 11, GM.SQUARE_LEAD.value, False),
        ],
        "STEMS_Pads_FX": [
            ("Pad_Main", 12, GM.POLYSYNTH.value, False),
            ("Pad_Warm", 12, GM.HALO_PAD.value, False),
            ("Pad_Evolve", 13, GM.SWEEP_PAD.value, False),
            ("Pad_Dark", 13, GM.METAL_PAD.value, False),
            ("Atmo_Space", 14, GM.FX_ATMOSPHERE.value, False),
            ("Atmo_SciFi", 14, GM.FX_SCI_FI.value, False),
            ("FX_Riser", 15, GM.FX_BRIGHTNESS.value, False),
            ("FX_Downer", 15, GM.FX_ECHOES.value, False),
            ("FX_Impact", 15, GM.FX_GOBLINS.value, False),
            ("Vocal_Chop", 15, GM.VOICE_LEAD.value, False),
            ("Glitch_Perc", 15, GM.FX_CRYSTAL.value, False),
        ],
    }
    
    generators = {
        "Kick_Main": gen.gen_kick_main,
        "Kick_Sub": gen.gen_kick_sub,
        "Kick_Click": gen.gen_kick_click,
        "Bass_Sub": gen.gen_bass_sub,
        "Bass_Main": gen.gen_bass_main,
        "Bass_FM": gen.gen_bass_fm,
        "Bass_Mid": gen.gen_bass_mid,
        "Bass_High": gen.gen_bass_high,
        "Bass_Reso": gen.gen_bass_reso,
        "HH_Closed_Main": gen.gen_hh_closed_main,
        "HH_Closed_Ghost": gen.gen_hh_closed_ghost,
        "HH_Open": gen.gen_hh_open,
        "HH_Ride": gen.gen_hh_ride,
        "Snare_Main": gen.gen_snare_main,
        "Snare_Ghost": gen.gen_snare_ghost,
        "Clap_Main": gen.gen_clap_main,
        "Clap_Layer": gen.gen_clap_layer,
        "Perc_Shaker": gen.gen_shaker,
        "Perc_Tambourine": gen.gen_tambourine,
        "Perc_Conga_Low": lambda t: gen.gen_congas(t, GM.CONGA_LOW.value),
        "Perc_Conga_High": lambda t: gen.gen_congas(t, GM.CONGA_HIGH.value, 0.2),
        "Crash_Main": lambda t: gen.gen_crash(t, GM.CRASH.value, 4),
        "Crash_FX": lambda t: gen.gen_crash(t, GM.CRASH.value, 8),
        "Lead_Main": gen.gen_lead_main,
        "Lead_Layer": gen.gen_lead_layer,
        "Seq_Main_16th": gen.gen_seq_16th,
        "Seq_Main_8th": gen.gen_seq_8th,
        "Seq_Counter": gen.gen_seq_counter,
        "Seq_Arp": gen.gen_seq_arp,
        "Seq_Pluck": gen.gen_seq_pluck,
        "Acid_Line": gen.gen_acid_line,
        "Pad_Main": gen.gen_pad_main,
        "Pad_Warm": gen.gen_pad_main,
        "Pad_Evolve": gen.gen_pad_evolve,
        "Pad_Dark": gen.gen_pad_evolve,
        "Atmo_Space": gen.gen_atmo_space,
        "Atmo_SciFi": gen.gen_atmo_space,
        "FX_Riser": gen.gen_fx_riser,
        "FX_Downer": gen.gen_fx_downer,
        "FX_Impact": gen.gen_fx_impact,
        "Vocal_Chop": gen.gen_vocal_chop,
        "Glitch_Perc": gen.gen_glitch_perc,
    }
    
    for stem_name, tracks in stem_groups.items():
        score = symusic.Score()
        score.ticks_per_quarter = config.tpq
        
        for name, channel, program, is_drum in tracks:
            track = symusic.Track()
            track.name = name
            track.program = program
            track.is_drum = is_drum
            
            if name in generators:
                generators[name](track)
            
            score.tracks.append(track)
        
        output_path = output_dir / f"{stem_name}.mid"
        score.dump_midi(str(output_path))
        print(f"  Created: {stem_name}.mid ({len(score.tracks)} tracks)")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    generate_variations()
    print("\n✅ Psytrance/Goa MIDI generation complete!")
    print(f"Files in: /home/baboon/psytrance-generator/midi/")