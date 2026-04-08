"""KubeCost-Gym Environment Client."""

from typing import Dict, Any

from openenv.core import EnvClient
from openenv.core.client_types import StepResult

from .models import Action, Observation


class KubeCostEnvClient(EnvClient[Action, Observation, Dict[str, Any]]):
    """Client for the KubeCost Environment."""

    def _step_payload(self, action: Action) -> Dict:
        return action.model_dump()

    def _parse_result(self, payload: Dict) -> StepResult[Observation]:
        obs_data = payload.get("observation", {})
        observation = Observation(**obs_data)
        
        return StepResult(
            observation=observation,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> Dict[str, Any]:
        return payload
