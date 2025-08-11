"""
Epsilon-Greedy multi-armed bandit implementation with an optional CLI simulator.

Usage (examples):
  python -m main --steps 1000 --epsilon 0.1 --env normal --k 10 --seed 42
  python -m main --steps 2000 --epsilon 0.05 --epsilon-decay 0.999 --env bernoulli --ps 0.1,0.5,0.9

This file can be used as a module (import classes) or executed as a script (CLI).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Iterable, Dict, Tuple
import argparse
import random
import math
import sys


@dataclass(frozen=True)
class Arm:
    name: str
    distribution: str  # "normal" or "bernoulli"
    p: Optional[float] = None  # For Bernoulli
    mu: Optional[float] = None  # For Normal
    sigma: float = 1.0  # For Normal

    def expected(self) -> float:
        if self.distribution == "bernoulli":
            assert self.p is not None
            return self.p
        if self.distribution == "normal":
            assert self.mu is not None
            return self.mu
        raise ValueError(f"Unknown distribution: {self.distribution}")

    def sample(self, rng: random.Random) -> float:
        if self.distribution == "bernoulli":
            assert self.p is not None
            return 1.0 if rng.random() < self.p else 0.0
        if self.distribution == "normal":
            assert self.mu is not None
            return rng.gauss(self.mu, self.sigma)
        raise ValueError(f"Unknown distribution: {self.distribution}")


class MultiArmedBandit:
    def __init__(self, arms: List[Arm], seed: Optional[int] = None) -> None:
        if not arms:
            raise ValueError("Arms list cannot be empty.")
        self.arms: List[Arm] = arms
        self._rng = random.Random(seed)

    def pull(self, action: int) -> float:
        if action < 0 or action >= len(self.arms):
            raise IndexError(
                f"Action {action} out of bounds for {len(self.arms)} arms.")
        return self.arms[action].sample(self._rng)

    @property
    def optimal_action(self) -> int:
        exps = [a.expected() for a in self.arms]
        max_val = max(exps)
        # Tie-break optimally among equals by picking the smallest index (deterministic)
        for i, v in enumerate(exps):
            if v == max_val:
                return i
        # Should never reach here
        return 0

    @property
    def k(self) -> int:
        return len(self.arms)


class EpsilonGreedyAgent:
    def __init__(
        self,
        n_actions: int,
        epsilon: float = 0.1,
        epsilon_min: float = 0.0,
        epsilon_decay: float = 1.0,
        initial_value: float = 0.0,
        step_size: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> None:
        if n_actions <= 0:
            raise ValueError("n_actions must be > 0.")
        if not (0.0 <= epsilon <= 1.0):
            raise ValueError("epsilon must be in [0,1].")
        if not (0.0 <= epsilon_min <= 1.0):
            raise ValueError("epsilon_min must be in [0,1].")
        if epsilon_decay <= 0.0:
            raise ValueError("epsilon_decay must be > 0.")
        if step_size is not None and not (0.0 < step_size <= 1.0):
            raise ValueError("step_size must be in (0,1] when provided.")

        self.n_actions: int = n_actions
        self.epsilon: float = float(epsilon)
        self.epsilon_min: float = float(epsilon_min)
        self.epsilon_decay: float = float(epsilon_decay)
        self.step_size: Optional[float] = step_size
        self.Q: List[float] = [float(initial_value)] * n_actions
        self.N: List[int] = [0] * n_actions
        self._rng = random.Random(seed)

    def _argmax_tiebreak(self, values: List[float]) -> int:
        max_val = max(values)
        candidates = [i for i, v in enumerate(values) if v == max_val]
        return self._rng.choice(candidates)

    def select_action(self) -> int:
        explore = self._rng.random() < self.epsilon
        if explore:
            return self._rng.randrange(self.n_actions)
        return self._argmax_tiebreak(self.Q)

    def update(self, action: int, reward: float) -> None:
        if action < 0 or action >= self.n_actions:
            raise IndexError(
                f"Action {action} out of bounds for n_actions={self.n_actions}.")

        self.N[action] += 1
        if self.step_size is None:
            alpha = 1.0 / self.N[action]
        else:
            alpha = self.step_size
        self.Q[action] += alpha * (reward - self.Q[action])
        # Decay epsilon after each step
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

    def reset(self, initial_value: float = 0.0) -> None:
        self.Q = [float(initial_value)] * self.n_actions
        self.N = [0] * self.n_actions

    def policy(self) -> List[float]:
        # Greedy policy with exploration is stochastic; we expose current Q estimates
        return list(self.Q)


def run_bandit(
    env: MultiArmedBandit,
    agent: EpsilonGreedyAgent,
    steps: int,
) -> Dict[str, object]:
    if steps <= 0:
        raise ValueError("steps must be > 0.")
    rewards: List[float] = []
    actions: List[int] = []
    optimal_hits = 0
    opt = env.optimal_action

    for t in range(steps):
        a = agent.select_action()
        r = env.pull(a)
        agent.update(a, r)

        actions.append(a)
        rewards.append(r)
        if a == opt:
            optimal_hits += 1

    avg_reward = sum(rewards) / steps
    optimal_rate = optimal_hits / steps
    return {
        "rewards": rewards,
        "actions": actions,
        "avg_reward": avg_reward,
        "optimal_action_rate": optimal_rate,
        "final_estimates": agent.policy(),
        "counts": list(agent.N),
        "epsilon_final": agent.epsilon,
        "optimal_action": opt,
    }


def _parse_float_list(s: str) -> List[float]:
    s = s.strip()
    if not s:
        return []
    try:
        return [float(x) for x in s.split(",")]
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid float list: {s}") from e


def _build_env(
    env_type: str,
    k: int,
    rng: random.Random,
    means: Optional[List[float]] = None,
    sigmas: Optional[List[float]] = None,
    ps: Optional[List[float]] = None,
    default_sigma: float = 1.0,
) -> MultiArmedBandit:
    arms: List[Arm] = []
    if env_type == "normal":
        if means is None:
            means = [rng.gauss(0.0, 1.0) for _ in range(k)]
        if sigmas is None:
            sigmas = [default_sigma] * len(means)
        if len(sigmas) != len(means):
            raise ValueError("Length of sigmas must match length of means.")
        for i, (mu, sigma) in enumerate(zip(means, sigmas)):
            if sigma <= 0:
                raise ValueError("Sigma must be > 0.")
            arms.append(
                Arm(name=f"arm_{i}", distribution="normal", mu=mu, sigma=float(sigma)))
    elif env_type == "bernoulli":
        if ps is None:
            ps = [rng.random() for _ in range(k)]
        for i, p in enumerate(ps):
            if not (0.0 <= p <= 1.0):
                raise ValueError("Bernoulli p must be in [0,1].")
            arms.append(
                Arm(name=f"arm_{i}", distribution="bernoulli", p=float(p)))
    else:
        raise ValueError("env must be one of: normal, bernoulli")
    return MultiArmedBandit(arms, seed=rng.randrange(2**63 - 1))


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="epsilon_greedy",
        description="Epsilon-Greedy multi-armed bandit simulator",
    )
    parser.add_argument("--steps", type=int, default=1000,
                        help="Number of interaction steps.")
    parser.add_argument("--epsilon", type=float,
                        default=0.1, help="Exploration rate.")
    parser.add_argument("--epsilon-decay", type=float, default=1.0,
                        help="Multiplicative epsilon decay per step.")
    parser.add_argument("--epsilon-min", type=float,
                        default=0.0, help="Lower bound for epsilon.")
    parser.add_argument("--initial-value", type=float, default=0.0,
                        help="Optimistic initial action-value estimates.")
    parser.add_argument("--step-size", type=float, default=None,
                        help="Constant step-size in (0,1]; if omitted, use sample-average.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed.")
    parser.add_argument(
        "--env", choices=["normal", "bernoulli"], default="normal", help="Environment type.")
    parser.add_argument("--k", type=int, default=10,
                        help="Number of arms (when not providing explicit params).")
    parser.add_argument("--means", type=_parse_float_list,
                        default=None, help="Comma-separated means for normal arms.")
    parser.add_argument("--sigmas", type=_parse_float_list,
                        default=None, help="Comma-separated sigmas for normal arms.")
    parser.add_argument("--ps", type=_parse_float_list, default=None,
                        help="Comma-separated Bernoulli probabilities.")
    parser.add_argument("--default-sigma", type=float, default=1.0,
                        help="Default sigma for normal env when sigmas not provided.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    # Validate some args
    if args.step_size is not None and not (0.0 < args.step_size <= 1.0):
        parser.error("--step-size must be in (0,1].")

    rng = random.Random(args.seed)
    env = _build_env(
        env_type=args.env,
        k=args.k if (args.means is None and args.ps is None) else (
            len(args.means) if args.means is not None else len(args.ps)),
        rng=rng,
        means=args.means,
        sigmas=args.sigmas,
        ps=args.ps,
        default_sigma=args.default_sigma,
    )

    agent = EpsilonGreedyAgent(
        n_actions=env.k,
        epsilon=args.epsilon,
        epsilon_min=args.epsilon_min,
        epsilon_decay=args.epsilon_decay,
        initial_value=args.initial_value,
        step_size=args.step_size,
        seed=rng.randrange(2**63 - 1),
    )

    results = run_bandit(env, agent, steps=args.steps)

    # Minimal summary
    print(f"Steps: {args.steps}")
    print(f"Avg reward: {results['avg_reward']:.6f}")
    print(f"Optimal action index: {results['optimal_action']}")
    print(f"Optimal action rate: {results['optimal_action_rate']:.3f}")
    print(f"Final epsilon: {results['epsilon_final']:.6f}")
    print("Final Q estimates:")
    for i, q in enumerate(results["final_estimates"]):
        print(f"  arm_{i}: {q:.6f} (count={results['counts'][i]})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
