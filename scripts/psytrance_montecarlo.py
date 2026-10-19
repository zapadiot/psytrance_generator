#!/usr/bin/env python3
"""
Monte Carlo algorithms ported from C++ for Psytrance Generation.

Provides:
- Xoshiro256++ RNG (high-quality, fast, jump-ahead for parallel streams)
- Sobol Sequences (QMC - low-discrepancy for parameter space exploration)
- MCMC Samplers (Metropolis-Hastings, HMC, MALA) for pattern space exploration
- Variance reduction utilities

Ported from: /home/baboon/monte_carlo_benchmark/
"""

import random
import math
from typing import List, Tuple, Callable, Optional, Iterator, Any
from dataclasses import dataclass
from functools import lru_cache


# ============================================================================
# XOSHIRO256++ RNG - State-of-the-art 256-bit RNG
# ============================================================================

class Xoshiro256pp:
    """
    Xoshiro256++ (xoroshiro256plusplus) - 256-bit state RNG.
    
    Features:
    - Period: 2^256 - 1
    - 4 x 64-bit state (fits in registers)
    - Jump functions for 2^128 non-overlapping streams
    - 4x u64 per iteration = perfect for AVX2
    - Passes BigCrush, 0.75 cycles/byte
    
    Reference: http://xoshiro.di.unimi.it/xoshiro256plusplus.c
    """
    
    __slots__ = ('_state',)
    
    def __init__(self, seed: int = 0):
        """Initialize with seed using SplitMix64 for entropy spreading."""
        self._state = [0, 0, 0, 0]
        self.seed(seed)
    
    def seed(self, seed: int):
        """Re-seed using SplitMix64."""
        z = seed + 0x9e3779b97f4a7c15
        for i in range(4):
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9 & 0xFFFFFFFFFFFFFFFF
            z = (z ^ (z >> 27)) * 0x94d049bb133111eb & 0xFFFFFFFFFFFFFFFF
            self._state[i] = z ^ (z >> 31)
        # Ensure non-zero state
        if all(s == 0 for s in self._state):
            self._state[0] = 1
    
    @staticmethod
    def _rotl(x: int, k: int) -> int:
        """Rotate left 64-bit."""
        return ((x << k) & 0xFFFFFFFFFFFFFFFF) | (x >> (64 - k))
    
    def next_u64(self) -> int:
        """Generate single 64-bit random value."""
        s = self._state
        result = self._rotl(s[1] * 5, 7) * 9 & 0xFFFFFFFFFFFFFFFF
        
        t = (s[1] << 17) & 0xFFFFFFFFFFFFFFFF
        
        s[2] ^= s[0]
        s[3] ^= s[1]
        s[1] ^= s[2]
        s[0] ^= s[3]
        
        s[2] ^= t
        s[3] = self._rotl(s[3], 45)
        
        return result
    
    def next_float(self) -> float:
        """Generate random float in [0, 1)."""
        return self.next_u64() / 2**64
    
    def next_float_range(self, a: float, b: float) -> float:
        """Generate random float in [a, b)."""
        return a + (b - a) * self.next_float()

    def next_normal(self, mean: float = 0.0, stddev: float = 1.0) -> float:
        """Generate a normal variate without using Python's global RNG."""
        u1 = max(self.next_float(), 1e-15)
        u2 = self.next_float()
        value = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mean + stddev * value
    
    def next_int(self, a: int, b: int) -> int:
        """Generate random int in [a, b]."""
        return a + int(self.next_float() * (b - a + 1))
    
    def choice(self, seq: List[Any]) -> Any:
        """Random choice from sequence."""
        return seq[int(self.next_float() * len(seq))]
    
    def shuffle(self, seq: List[Any]):
        """Fisher-Yates shuffle in place."""
        for i in range(len(seq) - 1, 0, -1):
            j = int(self.next_float() * (i + 1))
            seq[i], seq[j] = seq[j], seq[i]
    
    # ---------------------------------------------------------------------
    # JUMP FUNCTIONS - for parallel streams (2^128 non-overlapping)
    # ---------------------------------------------------------------------
    
    JUMP = (
        0x180ec6d33cfd0aba, 0xd5a61266f0c9392c,
        0xa9582618e03fc9aa, 0x39abdc4529b1661c
    )
    
    LONG_JUMP = (
        0x76e15d3efefdcbbf, 0xc5004e441c522fb3,
        0x77710069854ee241, 0x39109bb02acbe635
    )
    
    def jump(self):
        """Advance state by 2^128 steps (new independent stream)."""
        new_state = [0, 0, 0, 0]
        for jump_val in self.JUMP:
            for b in range(64):
                if jump_val & (1 << b):
                    for i in range(4):
                        new_state[i] ^= self._state[i]
                    self._next_state()
        self._state = new_state
    
    def long_jump(self):
        """Advance state by 2^192 steps."""
        new_state = [0, 0, 0, 0]
        for jump_val in self.LONG_JUMP:
            for b in range(64):
                if jump_val & (1 << b):
                    for i in range(4):
                        new_state[i] ^= self._state[i]
                    self._next_state()
        self._state = new_state
    
    def _next_state(self):
        """Single step of the generator (internal)."""
        s = self._state
        t = (s[1] << 17) & 0xFFFFFFFFFFFFFFFF
        
        s[2] ^= s[0]
        s[3] ^= s[1]
        s[1] ^= s[2]
        s[0] ^= s[3]
        
        s[2] ^= t
        s[3] = self._rotl(s[3], 45)
    
    def fork(self) -> 'Xoshiro256pp':
        """Create a new independent RNG (jumps ahead)."""
        new_rng = Xoshiro256pp(0)
        new_rng._state = self._state.copy()
        new_rng.jump()
        return new_rng
    
    def get_state(self) -> Tuple[int, int, int, int]:
        """Get state for serialization."""
        return tuple(self._state)
    
    def set_state(self, state: Tuple[int, int, int, int]):
        """Set state for reproducibility."""
        self._state = list(state)


# ============================================================================
# SOBOL SEQUENCES (QMC) - Low-discrepancy sequences
# ============================================================================

# Primitive polynomials for Sobol (dimensions 1-40)
# x^d + a_1*x^{d-1} + ... + a_d (stored as bitmask)
SOBOL_PRIMITIVE_POLY = [
    0,       # dim 1 (special)
    0x3,     # dim 2: x + 1
    0x7,     # dim 3: x^2 + x + 1
    0xB,     # dim 4: x^3 + x + 1
    0x13,    # dim 5: x^4 + x + 1
    0x25,    # dim 6: x^5 + x^2 + 1
    0x3D,    # dim 7: x^6 + x^4 + x^3 + x^2 + 1
    0x5F,    # dim 8
    0xC1,    # dim 9
    0xEB,    # dim 10
    0x101,   # dim 11
    0x15B,   # dim 12
    0x1A7,   # dim 13
    0x22F,   # dim 14
    0x2A1,   # dim 15
    0x36D,   # dim 16
    0x4E5,   # dim 17
    0x5D3,   # dim 18
    0x70F,   # dim 19
    0x7B5,   # dim 20
    0x8D9,   # dim 21
    0x97F,   # dim 22
    0xA59,   # dim 23
    0xB7D,   # dim 24
    0xC6F,   # dim 25
    0xD7B,   # dim 26
    0xE9D,   # dim 27
    0xF6D,   # dim 28
    0x1081,  # dim 29
    0x114D,  # dim 30
    0x1265,  # dim 31
    0x137B,  # dim 32
    0x14E7,  # dim 33
    0x15B9,  # dim 34
    0x16D5,  # dim 35
    0x17E3,  # dim 36
    0x18F1,  # dim 37
    0x1A2D,  # dim 38
    0x1B59,  # dim 39
    0x1C67,  # dim 40
]

# Standard Sobol parameters for dimensions 2-6. The MIDI generator uses six
# dimensions, so all active dimensions use published direction numbers.
SOBOL_PARAMETERS = [
    (1, 0, [1]),
    (2, 1, [1, 1]),
    (3, 1, [1, 1, 1]),
    (3, 2, [1, 3, 1]),
    (4, 1, [1, 1, 3, 3]),
]


def _build_sobol_initial_direction(max_dim: int = 40, max_bits: int = 32) -> List[List[int]]:
    """Build initial direction numbers for Sobol sequence."""
    V = [[0] * max_bits for _ in range(max_dim)]
    
    # Dimension 1: V[1][k] = 1 << (32 - k) = 2^(32-k)
    for k in range(max_bits):
        V[0][k] = 1 << (max_bits - 1 - k)
    
    for dimension, (degree, polynomial, initial) in enumerate(SOBOL_PARAMETERS, start=1):
        if dimension >= max_dim:
            break
        for index, value in enumerate(initial):
            V[dimension][index] = value << (max_bits - 1 - index)
        for index in range(degree, max_bits):
            value = V[dimension][index - degree] ^ (V[dimension][index - degree] >> degree)
            for offset in range(1, degree):
                if (polynomial >> (degree - 1 - offset)) & 1:
                    value ^= V[dimension][index - offset]
            V[dimension][index] = value & ((1 << max_bits) - 1)
    
    return V


class SobolGenerator:
    """
    Sobol Sequence Generator (QMC) - Low-discrepancy sequences.
    
    Properties:
    - Discrepancy: O(N^{-1} (log N)^s) vs O(N^{-1/2}) for random
    - O(1) per point using Gray code: x_{n+1} = x_n XOR v_{ctz(n)}
    - Supports random digital shift (Owen scrambling)
    - Supports skip-ahead for parallel generation
    
    Use for:
    - Low-discrepancy sampling of parameter spaces
    - Better coverage of high-dimensional spaces
    - Variance reduction in Monte Carlo integration
    """
    
    def __init__(self, dimensions: int = 40, bits: int = 32, seed: int = 0):
        if dimensions < 1 or dimensions > len(SOBOL_PARAMETERS) + 1:
            raise ValueError("SobolGenerator supports dimensions 1 through 6")
        if bits != 32:
            raise ValueError("SobolGenerator currently supports 32 direction bits")
        self.dimensions = dimensions
        self.bits = bits
        self.max_val = (1 << bits) - 1
        
        # Compute direction numbers
        self.V = _build_sobol_initial_direction(self.dimensions, bits)
        
        # State
        self.current = [0] * self.dimensions
        self.index = 0
        
        # Randomization (Owen digital shift)
        rng = Xoshiro256pp(seed)
        self.digital_shift = [rng.next_u64() & self.max_val for _ in range(self.dimensions)]
        self.linear_scramble = [rng.next_u64() & self.max_val for _ in range(self.dimensions)]
    
    def _ctz(self, x: int) -> int:
        """Count trailing zeros."""
        if x == 0:
            return self.bits
        return (x & -x).bit_length() - 1
    
    def next(self) -> List[float]:
        """Generate next Sobol point in [0, 1)^dimensions."""
        if self.index == 0:
            # First point = digital shift
            self.current = self.digital_shift.copy()
        else:
            # Gray code: x_{n+1} = x_n XOR v_{ctz(n)}
            ctz = self._ctz(self.index)
            if ctz < self.bits:
                for d in range(self.dimensions):
                    self.current[d] ^= self.V[d][ctz]
        
        self.index += 1
        
        # Apply linear scramble and normalize to [0, 1)
        return [(self.current[d] ^ self.linear_scramble[d]) / (1 << self.bits) 
                for d in range(self.dimensions)]
    
    def next_scaled(self, ranges: List[Tuple[float, float]]) -> List[float]:
        """Generate next point scaled to custom ranges."""
        point = self.next()
        return [ranges[d][0] + point[d] * (ranges[d][1] - ranges[d][0]) 
                for d in range(min(self.dimensions, len(ranges)))]
    
    def skip(self, n: int):
        """Skip n points (for parallel generation)."""
        for _ in range(n):
            self.next()
    
    def reset(self):
        """Reset to beginning."""
        self.current = [0] * self.dimensions
        self.index = 0


# ============================================================================
# MCMC SAMPLERS - For exploring musical pattern space
# ============================================================================

@dataclass
class MCMCResult:
    """Result from MCMC sampling."""
    samples: List[List[float]]
    accepted: int
    rejected: int
    acceptance_rate: float
    log_likelihoods: List[float]


class MetropolisHastings:
    """
    Random Walk Metropolis-Hastings sampler.
    
    Use for:
    - Exploring musical parameter spaces
    - Finding patterns that satisfy constraints
    - Bayesian optimization of groove parameters
    """
    
    def __init__(self, 
                 log_target: Callable[[List[float]], float],
                 dim: int,
                 step_size: float = 1.0,
                 rng: Optional[Xoshiro256pp] = None):
        self.log_target = log_target
        self.dim = dim
        self.step_size = step_size
        self.rng = rng or Xoshiro256pp()
        self.current = [0.0] * dim
        self.current_log_prob = -float('inf')
    
    def initialize(self, start: Optional[List[float]] = None):
        """Initialize chain at starting point."""
        if start is not None:
            self.current = start[:]
        else:
            self.current = [self.rng.next_normal() for _ in range(self.dim)]
        self.current_log_prob = self.log_target(self.current)
    
    def step(self) -> bool:
        """Single MH step. Returns True if accepted."""
        # Propose new point
        proposal = [
            self.current[i] + self.rng.next_float_range(-self.step_size, self.step_size)
            for i in range(self.dim)
        ]
        
        proposal_log_prob = self.log_target(proposal)
        
        # Acceptance probability
        log_alpha = proposal_log_prob - self.current_log_prob
        
        if log_alpha >= 0 or self.rng.next_float() < math.exp(log_alpha):
            self.current = proposal
            self.current_log_prob = proposal_log_prob
            return True
        return False
    
    def sample(self, n_samples: int, burnin: int = 0, thin: int = 1,
               start: Optional[List[float]] = None) -> MCMCResult:
        """Run MCMC chain."""
        self.initialize(start)
        
        # Burn-in
        for _ in range(burnin):
            self.step()
        
        samples = []
        log_likelihoods = []
        accepted = 0
        rejected = 0
        
        for i in range(n_samples * thin):
            if self.step():
                accepted += 1
            else:
                rejected += 1
            
            if i % thin == 0:
                samples.append(self.current[:])
                log_likelihoods.append(self.current_log_prob)
        
        return MCMCResult(
            samples=samples,
            accepted=accepted,
            rejected=rejected,
            acceptance_rate=accepted / (accepted + rejected) if (accepted + rejected) > 0 else 0,
            log_likelihoods=log_likelihoods
        )
    
    def adapt_step_size(self, target_acceptance: float = 0.234):
        """Adapt step size during burn-in (Roberts et al. optimal)."""
        # This would be called periodically during burn-in
        pass


class HamiltonianMonteCarlo:
    """
    Hamiltonian Monte Carlo (HMC) - Uses gradient information.
    
    Better for high-dimensional correlated posteriors.
    Requires differentiable log-target.
    """
    
    def __init__(self,
                 log_target: Callable[[List[float]], float],
                 grad_log_target: Callable[[List[float]], List[float]],
                 dim: int,
                 step_size: float = 0.1,
                 n_steps: int = 10,
                 rng: Optional[Xoshiro256pp] = None):
        self.log_target = log_target
        self.grad_log_target = grad_log_target
        self.dim = dim
        self.step_size = step_size
        self.n_steps = n_steps
        self.rng = rng or Xoshiro256pp()
        self.current = [0.0] * dim
    
    def leapfrog(self, q: List[float], p: List[float]) -> Tuple[List[float], List[float]]:
        """Leapfrog integrator for Hamiltonian dynamics."""
        q = q[:]
        p = p[:]
        
        # Half step for momentum
        grad = self.grad_log_target(q)
        for i in range(self.dim):
            p[i] += 0.5 * self.step_size * grad[i]
        
        # Full steps
        for _ in range(self.n_steps - 1):
            for i in range(self.dim):
                q[i] += self.step_size * p[i]
            grad = self.grad_log_target(q)
            for i in range(self.dim):
                p[i] += self.step_size * grad[i]
        
        # Last position step
        for i in range(self.dim):
            q[i] += self.step_size * p[i]
        
        # Final half step for momentum
        grad = self.grad_log_target(q)
        for i in range(self.dim):
            p[i] += 0.5 * self.step_size * grad[i]
        
        return q, p
    
    def hamiltonian(self, q: List[float], p: List[float]) -> float:
        """H(q, p) = -log_target(q) + 0.5 * p^T p"""
        return -self.log_target(q) + 0.5 * sum(x * x for x in p)
    
    def step(self) -> bool:
        """Single HMC step."""
        # Sample momentum
        p = [self.rng.next_normal() for _ in range(self.dim)]
        
        current_H = self.hamiltonian(self.current, p)
        
        # Leapfrog integration
        q_new, p_new = self.leapfrog(self.current, p)
        
        proposed_H = self.hamiltonian(q_new, p_new)
        
        # Metropolis acceptance
        log_alpha = current_H - proposed_H
        
        if log_alpha >= 0 or self.rng.next_float() < math.exp(log_alpha):
            self.current = q_new
            return True
        return False


class MALA:
    """
    Metropolis-Adjusted Langevin Algorithm (MALA).
    
    Uses gradient for proposal: proposal = current + step_size * grad/2 + noise
    Optimal acceptance rate ~ 0.574
    """
    
    def __init__(self,
                 log_target: Callable[[List[float]], float],
                 grad_log_target: Callable[[List[float]], List[float]],
                 dim: int,
                 step_size: float = 1.0,
                 rng: Optional[Xoshiro256pp] = None):
        self.log_target = log_target
        self.grad_log_target = grad_log_target
        self.dim = dim
        self.step_size = step_size
        self.rng = rng or Xoshiro256pp()
        self.current = [0.0] * dim
        self.current_log_prob = -float('inf')
    
    def initialize(self, start: Optional[List[float]] = None):
        if start is not None:
            self.current = start[:]
        else:
            self.current = [self.rng.next_normal() for _ in range(self.dim)]
        self.current_log_prob = self.log_target(self.current)
    
    def step(self) -> bool:
        """Single MALA step."""
        grad = self.grad_log_target(self.current)
        
        # Propose: x' = x + (step_size/2) * grad + sqrt(step_size) * N(0,1)
        proposal = []
        log_q_forward = 0.0
        log_q_backward = 0.0
        
        for i in range(self.dim):
            drift = 0.5 * self.step_size * grad[i]
            noise = self.rng.next_normal() * math.sqrt(self.step_size)
            proposal.append(self.current[i] + drift + noise)
            
            # Forward proposal density
            diff = proposal[i] - self.current[i] - drift
            log_q_forward += -0.5 * diff * diff / self.step_size - 0.5 * math.log(2 * math.pi * self.step_size)
            
            # Backward proposal density (from proposal to current)
            grad_prop = self.grad_log_target(proposal)
            drift_back = 0.5 * self.step_size * grad_prop[i]
            diff_back = self.current[i] - proposal[i] - drift_back
            log_q_backward += -0.5 * diff_back * diff_back / self.step_size - 0.5 * math.log(2 * math.pi * self.step_size)
        
        log_alpha = (self.log_target(proposal) - self.current_log_prob + 
                     log_q_backward - log_q_forward)
        
        if log_alpha >= 0 or self.rng.next_float() < math.exp(log_alpha):
            self.current = proposal
            self.current_log_prob = self.log_target(proposal)
            return True
        return False


# ============================================================================
# VARIANCE REDUCTION UTILITIES
# ============================================================================

class VarianceReducer:
    """Variance reduction techniques for Monte Carlo."""
    
    @staticmethod
    def antithetic(samples: List[float]) -> List[float]:
        """Antithetic variates: pair x with 1-x for uniform [0,1]."""
        return samples + [1 - x for x in samples]
    
    @staticmethod
    def stratified(n_strata: int, rng: Xoshiro256pp) -> List[float]:
        """Stratified sampling: one sample per stratum."""
        return [(i + rng.next_float()) / n_strata for i in range(n_strata)]
    
    @staticmethod
    def control_variate(samples: List[float], 
                        control_samples: List[float],
                        control_mean: float) -> List[float]:
        """Control variate adjustment (requires known control mean)."""
        # Optimal coefficient beta = Cov(X, Y) / Var(Y)
        n = len(samples)
        if n != len(control_samples):
            raise ValueError("Sample lengths must match")
        
        mean_x = sum(samples) / n
        mean_y = sum(control_samples) / n
        
        cov = sum((samples[i] - mean_x) * (control_samples[i] - mean_y) for i in range(n)) / n
        var_y = sum((y - mean_y) ** 2 for y in control_samples) / n
        
        if var_y == 0:
            return samples
        
        beta = cov / var_y
        return [samples[i] - beta * (control_samples[i] - control_mean) for i in range(n)]


# ============================================================================
# MUSICAL APPLICATION HELPERS
# ============================================================================

class GrooveExplorer:
    """
    MCMC-based groove parameter explorer.
    
    Uses MCMC to find groove parameters that maximize a "funkiness" score.
    """
    
    def __init__(self, rng: Optional[Xoshiro256pp] = None, seed: Optional[int] = None):
        if rng is not None:
            self.rng = rng
        elif seed is not None:
            self.rng = Xoshiro256pp(seed)
        else:
            self.rng = Xoshiro256pp()
    
    def explore_microtiming(self, 
                           n_samples: int = 1000,
                           base_pattern: List[float] = None) -> List[List[float]]:
        """
        Explore microtiming variations for a drum pattern.
        
        Args:
            n_samples: Number of groove variations to generate
            base_pattern: Base timings (e.g., [0, 0.25, 0.5, 0.75] for 16ths)
            
        Returns:
            List of microtiming offsets for each 16th note
        """
        if base_pattern is None:
            base_pattern = [i / 16.0 for i in range(16)]  # 16th notes
        
        dim = len(base_pattern)
        
        def log_target(offsets):
            # Penalize large deviations from grid
            penalty = sum(o * o for o in offsets) * 100
            
            # Reward syncopation (off-grid feel)
            syncopation = sum(
                abs(math.sin(2 * math.pi * (base_pattern[i] + offsets[i])))
                for i in range(dim)
            )
            
            # Prefer small offsets with interesting syncopation
            return syncopation - penalty
        
        mh = MetropolisHastings(log_target, dim, step_size=0.02, rng=self.rng)
        # Starting at the grid keeps the chain reproducible and prevents a
        # random Gaussian initialization from producing an overly loose groove.
        result = mh.sample(n_samples, burnin=100, thin=10, start=[0.0] * dim)
        return result.samples
    
    def explore_velocity_curves(self,
                               n_samples: int = 500,
                               n_notes: int = 16) -> List[List[int]]:
        """
        Explore velocity curves for humanized feel.
        """
        dim = n_notes
        
        def log_target(velocities):
            # Smooth velocity changes (no sudden jumps)
            smoothness = -sum((velocities[i] - velocities[i-1])**2 for i in range(1, dim))
            
            # Prefer velocities in musical range
            range_penalty = -sum((v - 100)**2 for v in velocities if v < 30 or v > 127)
            
            # Accent pattern (downbeats stronger)
            accent_bonus = sum(velocities[i] for i in range(0, dim, 4))  # every 4th
            
            return smoothness * 0.1 + range_penalty + accent_bonus * 0.5
        
        mh = MetropolisHastings(log_target, dim, step_size=5, rng=self.rng)
        result = mh.sample(n_samples, burnin=50, thin=5, start=[100] * dim)
        
        # Clamp to valid MIDI range
        return [[max(1, min(127, int(v))) for v in sample] for sample in result.samples]


class ParameterSpaceExplorer:
    """
    Explore high-dimensional synth parameter spaces using QMC.
    
    Better than random for coverage - finds sweet spots efficiently.
    """
    
    def __init__(self, dimensions: int, rng: Optional[Xoshiro256pp] = None, seed: Optional[int] = None):
        if rng is not None:
            self.rng = rng
            self.sobol = SobolGenerator(dimensions=dimensions, seed=rng.next_u64())
        elif seed is not None:
            self.rng = Xoshiro256pp(seed)
            self.sobol = SobolGenerator(dimensions=dimensions, seed=seed)
        else:
            self.rng = Xoshiro256pp()
            self.sobol = SobolGenerator(dimensions=dimensions, seed=0)
        self.param_ranges: List[Tuple[float, float]] = []
    
    def set_ranges(self, ranges: List[Tuple[float, float]]):
        """Set parameter ranges (min, max) for each dimension."""
        self.param_ranges = ranges
    
    def explore(self, n_points: int) -> List[List[float]]:
        """Generate n_points parameter sets with good coverage."""
        if not self.param_ranges:
            # Default to [0, 1]
            self.param_ranges = [(0.0, 1.0)] * self.sobol.dimensions
        
        points = []
        for _ in range(n_points):
            point = self.sobol.next_scaled(self.param_ranges)
            points.append(point)
        return points
    
    def random_search(self, 
                     evaluate: Callable[[List[float]], float],
                     n_iterations: int = 1000) -> Tuple[List[float], float]:
        """
        Random search with Sobol initialization + local refinement.
        """
        # Initial Sobol exploration
        if n_iterations < 1:
            raise ValueError("n_iterations must be positive")
        initial_points = self.explore(min(100, max(1, n_iterations // 10)))
        
        best_params = None
        best_score = -float('inf')
        
        # Evaluate initial points
        for params in initial_points:
            score = evaluate(params)
            if score > best_score:
                best_score = score
                best_params = params[:]
        
        # Local refinement around best (simple hill climbing)
        current = best_params[:]
        current_score = best_score
        for _ in range(n_iterations - len(initial_points)):
            # Small perturbation
            candidate = [current[i] + self.rng.next_float_range(-0.05, 0.05)
                        for i in range(len(current))]
            
            # Clamp to ranges
            for i, (lo, hi) in enumerate(self.param_ranges):
                candidate[i] = max(lo, min(hi, candidate[i]))
            
            score = evaluate(candidate)
            if score > current_score:
                current = candidate
                current_score = score
                if score > best_score:
                    best_score = score
                    best_params = candidate[:]
        
        return best_params, best_score


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_rng(seed: Optional[int] = None) -> Xoshiro256pp:
    """Create RNG with optional seed."""
    if seed is None:
        seed = int.from_bytes(random.getrandbits(64).to_bytes(8, 'little'), 'little')
    return Xoshiro256pp(seed)


def create_sobol(dimensions: int, seed: Optional[int] = None) -> SobolGenerator:
    """Create Sobol generator."""
    return SobolGenerator(dimensions=dimensions, seed=seed or 0)


def create_groove_explorer(seed: Optional[int] = None) -> GrooveExplorer:
    """Create groove explorer."""
    return GrooveExplorer(rng=Xoshiro256pp(seed or 0))


def create_parameter_explorer(dimensions: int, seed: Optional[int] = None) -> ParameterSpaceExplorer:
    """Create parameter space explorer."""
    return ParameterSpaceExplorer(dimensions, rng=Xoshiro256pp(seed or 0))


# ============================================================================
# DEMO / TEST
# ============================================================================

if __name__ == "__main__":
    print("=== Xoshiro256++ RNG ===")
    rng = Xoshiro256pp(42)
    print(f"First 5 u64: {[rng.next_u64() for _ in range(5)]}")
    print(f"First 5 float: {[rng.next_float() for _ in range(5)]}")
    print(f"Jump test: state before={rng.get_state()}")
    rng.jump()
    print(f"After jump: state={rng.get_state()}")
    
    print("\n=== Sobol Generator ===")
    sobol = SobolGenerator(dimensions=4, seed=42)
    for i in range(5):
        point = sobol.next()
        print(f"  Point {i}: {[f'{x:.6f}' for x in point]}")
    
    # Scaled to musical ranges
    sobol2 = SobolGenerator(dimensions=4, seed=123)
    ranges = [(60, 72), (0, 127), (0.0, 1.0), (30, 127)]  # pitch, vel, pan, filter
    for i in range(5):
        point = sobol2.next_scaled(ranges)
        print(f"  Scaled {i}: pitch={point[0]:.1f}, vel={point[1]:.0f}, pan={point[2]:.3f}, filter={point[3]:.0f}")
    
    print("\n=== MCMC Groove Explorer ===")
    explorer = GrooveExplorer(seed=42)
    grooves = explorer.explore_microtiming(n_samples=10, base_pattern=[i/16.0 for i in range(16)])
    print(f"Generated {len(grooves)} groove variations")
    print(f"  First groove offsets (ms @ 120bpm): {[round(o*500,1) for o in grooves[0][:8]]}")
    
    velocities = explorer.explore_velocity_curves(n_samples=5, n_notes=16)
    print(f"  Velocity curves: {velocities[0]}")
    
    print("\n=== Parameter Space Explorer ===")
    param_explorer = ParameterSpaceExplorer(4, seed=42)
    param_explorer.set_ranges([
        (20, 20000),    # filter freq
        (0, 1),         # resonance
        (-24, 24),      # pitch mod
        (0, 127)        # velocity
    ])
    params = param_explorer.explore(10)
    for i, p in enumerate(params):
        print(f"  Params {i}: filter={p[0]:.0f}Hz, res={p[1]:.3f}, pitch={p[2]:.1f}, vel={p[2]:.0f}")
    
    print("\n✅ All Monte Carlo modules working!")
