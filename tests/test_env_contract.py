import pytest

from env import KubeCostEnv
from graders import ColdStartGrader, EfficientSqueezeGrader, EntropyStormGrader
from models import Action, ActionType, EnvState, Observation


def test_reset_returns_observation_and_state_type():
    env = KubeCostEnv("traces/trace_v1_coldstart.json")
    obs = env.reset()
    assert isinstance(obs, Observation)

    state = env.state()
    assert isinstance(state, EnvState)
    assert state.step == 0


def test_step_applies_scale_action_to_observation():
    env = KubeCostEnv("traces/trace_v1_coldstart.json")
    obs0 = env.reset()
    initial_replicas = obs0.active_replicas

    # scale up by 5 and verify the next observation reflects action overlay
    obs1, reward, done, info = env.step(Action(action_type=ActionType.SCALE_UP_5))
    assert isinstance(obs1, Observation)
    assert obs1.active_replicas == initial_replicas + 5
    assert 0.0 <= reward <= 10.5


def test_dot_run_trajectory_and_logout_consistency():
    env = KubeCostEnv("traces/trace_v1_coldstart.json")
    _ = env.reset()
    for i in range(3):
        env.step(Action(action_type=ActionType.MAINTAIN))

    trajectory = env.trajectory
    assert len(trajectory) == 3
    assert all(step.observation.p99_latency_ms >= 0.0 for step in trajectory)


def test_graders_clamp_scores():
    empty = []
    assert ColdStartGrader().grade(empty) == 0.0
    assert EfficientSqueezeGrader().grade(empty) == 0.0
    assert EntropyStormGrader().grade(empty) == 0.0

    # fabricated trajectory with full violations
    class FakeStep:
        def __init__(self, steal, err):
            self.observation = type("Obs", (), {"cpu_steal_pct": steal, "http_error_rate": err})
            self.action = ActionType.MAINTAIN
            self.reward = 0.0
            self.done = False
            self.info = {}

    traj = [FakeStep(0.5, 1.0) for _ in range(10)]
    assert 0.0 <= EfficientSqueezeGrader().grade(traj) <= 1.0
    assert 0.0 <= ColdStartGrader().grade(traj) <= 1.0
