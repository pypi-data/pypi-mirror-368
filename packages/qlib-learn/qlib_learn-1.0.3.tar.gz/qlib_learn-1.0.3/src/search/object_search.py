"""
Object search environment for reinforcement learning agents.

This module defines the `ObjectSearch` class, which represents an environment
where an agent navigates a 2D grid to locate a target object. The environment
is customizable via observation spaces, action spaces, reward strategies,
and entity locator strategies.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from typing import Dict, Tuple

from ..agent.my_agent import MyAgent
from ..controllers.action_space import ActionSpace
from ..global_typing import PosType, StateType
from ..locators.locator_interface import LocatorStrategy
from ..reward_strategy.reward_interface import RewardStrategy
from ..spaces.observation_space import ObservationSpace


class ObjectSearch:
    """
    Represents an object search environment in a 2D grid.

    The environment contains an agent and a target entity placed in the grid.
    The agent moves according to the provided action space, and rewards are
    computed based on a given reward strategy.

    Attributes:
        obs (ObservationSpace): The observation space storing entities and their positions.
        actions (ActionSpace): The set of possible actions the agent can take.
        agent (MyAgent): The agent instance interacting with the environment.
        reward_strategy (RewardStrategy): Strategy for computing rewards per step.
        locators (Dict[str, LocatorStrategy]): Strategies for locating entities in the grid.
        agent_name (str): Name of the agent entity in the observation space.
        target_name (str): Name of the target entity in the observation space.
        agent_pos (Tuple[int, int]): Current position of the agent.
        target_pos (Tuple[int, int]): Current position of the target.
    """

    def __init__(
        self,
        observartion_space: ObservationSpace,
        action_space: ActionSpace,
        agent: MyAgent,
        reward_strategy: RewardStrategy,
        locators: Dict[str, LocatorStrategy],
        agent_name: str,
        target_name: str,
    ) -> None:
        """
        Initializes the ObjectSearch environment.

        Args:
            observartion_space (ObservationSpace): The observation space for entities.
            action_space (ActionSpace): Available actions for the agent.
            agent (MyAgent): Agent instance to control.
            reward_strategy (RewardStrategy): Strategy for computing rewards.
            locators (Dict[str, LocatorStrategy]): Mapping of entity names to their locator strategies.
            agent_name (str): Name of the agent entity.
            target_name (str): Name of the target entity.
        """
        self.obs = observartion_space
        self.actions = action_space
        self.agent = agent
        self.reward_strategy = reward_strategy
        self.locators = locators

        self.agent_name = agent_name
        self.target_name = target_name

        self.reset()

    def _search(self) -> None:
        """
        Places all entities in the observation space at valid positions.

        Ensures that no two entities occupy the same position.
        """
        occupied = set()

        for entity in self.obs.entities:
            locator = self.locators[entity]

            while True:
                position = locator.locate(self.obs.shape[:2])
                if position not in occupied:
                    break

            occupied.add(position)
            self.obs.set_entity(entity, position)

    def get_state(self) -> StateType:
        """
        Retrieves the current state of the environment.

        Returns:
            Tuple[Tuple[int, int], Tuple[int, int]]:
                A tuple containing the agent's position and the target's position.
        """
        return (self.agent_pos, self.target_pos)

    def reset(self) -> None:
        """
        Resets the environment for a new episode.

        Clears all entities, places them in new valid positions,
        and updates the agent and target positions.
        """
        for entity in self.obs.entities:
            self.obs.clear_entity(entity)

        self._search()
        self.agent_pos: PosType = self.locators[self.agent_name].locate(
            self.obs.shape[:2]
        )
        self.target_pos: PosType = self.locators[self.target_name].locate(
            self.obs.shape[:2]
        )

    def step(self, action: int) -> Tuple[float, bool]:
        """
        Executes one step in the environment given an action.

        Args:
            action (int): Index of the action to execute.

        Returns:
            Tuple[float, bool]:
                - reward (float): The computed reward for this step.
                - terminated (bool): Whether the episode has ended
                  (agent has reached the target).
        """
        old_agent_pos = self.agent_pos
        attempted_new_agent_pos = self.actions[action](*old_agent_pos)

        # Move the agent only if within bounds
        if (
            0 <= attempted_new_agent_pos[0] < self.obs.shape[0]
            and 0 <= attempted_new_agent_pos[1] < self.obs.shape[1]
        ):
            self.agent_pos = attempted_new_agent_pos

        reward = self.reward_strategy.compute(
            (self.agent_pos, self.target_pos),
            (attempted_new_agent_pos, self.target_pos),
        )

        terminated = self.agent_pos == self.target_pos
        return reward, terminated
