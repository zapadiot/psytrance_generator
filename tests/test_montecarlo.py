import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.psytrance_generator import PsyConfig, generate_psytrance_midi
from scripts.psytrance_montecarlo import (
    GrooveExplorer,
    ParameterSpaceExplorer,
    SobolGenerator,
    Xoshiro256pp,
)


class MonteCarloTests(unittest.TestCase):
    def test_seeded_rng_and_groove_are_reproducible(self):
        first = Xoshiro256pp(123)
        second = Xoshiro256pp(123)
        self.assertEqual(
            [first.next_normal() for _ in range(8)],
            [second.next_normal() for _ in range(8)],
        )
        self.assertEqual(
            GrooveExplorer(seed=123).explore_microtiming(2),
            GrooveExplorer(seed=123).explore_microtiming(2),
        )

    def test_sobol_points_are_bounded_and_vary_by_dimension(self):
        first = SobolGenerator(dimensions=6, seed=123)
        second = SobolGenerator(dimensions=6, seed=123)
        points = [first.next() for _ in range(32)]
        self.assertEqual(points, [second.next() for _ in range(32)])
        self.assertTrue(all(0.0 <= value < 1.0 for point in points for value in point))
        self.assertGreater(len({tuple(point) for point in points}), 1)
        with self.assertRaises(ValueError):
            SobolGenerator(dimensions=7)

    def test_small_parameter_search_is_valid(self):
        explorer = ParameterSpaceExplorer(2, seed=9)
        explorer.set_ranges([(0.0, 1.0), (0.0, 1.0)])
        params, score = explorer.random_search(lambda values: -sum(values), 1)
        self.assertEqual(len(params), 2)
        self.assertLessEqual(score, 0.0)

    def test_midi_variation_is_seeded_and_bounded(self):
        config = PsyConfig(bpm=145, bars=1)
        with tempfile.TemporaryDirectory() as directory:
            first_path = Path(directory) / "first.mid"
            second_path = Path(directory) / "second.mid"
            first = generate_psytrance_midi(
                first_path, config, "A", "double_harmonic", 77, True
            )
            generate_psytrance_midi(
                second_path, config, "A", "double_harmonic", 77, True
            )
            self.assertEqual(
                hashlib.sha256(first_path.read_bytes()).digest(),
                hashlib.sha256(second_path.read_bytes()).digest(),
            )
            for track in first.tracks:
                for note in track.notes:
                    self.assertGreaterEqual(note.time, 0)
                    self.assertLess(note.time, config.total_ticks)
                    self.assertGreaterEqual(note.pitch, 0)
                    self.assertLessEqual(note.pitch, 127)


if __name__ == "__main__":
    unittest.main()
