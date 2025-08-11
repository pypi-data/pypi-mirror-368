"""
Defines the main agent class for the Q-Learning algorithm.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

import numpy as np

from ..controllers.action_space import ActionSpace
from ..global_typing import NumericType
from .epsilon_greedy_policy import EpsilonGreedyPolicy
from .Q import QTable
from .typing import TrainStateType


class MyAgent:
    """
    Represents a Q-Learning agent that learns optimal policies.

    Attributes:
        actions (ActionSpace): The available action space.
        policy (EpsilonGreedyPolicy): The policy strategy for action selection.
        q_table (QTable): The Q-value table for state-action pairs.
        lr (float): Learning rate.
        gamma (float): Discount factor for future rewards.
    """

    def __init__(
        self,
        actions: ActionSpace,
        policy: EpsilonGreedyPolicy,
        lr: float = 0.1,
        gamma: float = 0.9,
    ):
        """
        Initializes the agent with given parameters.

        Args:
            actions (ActionSpace): The available actions for the agent.
            policy (EpsilonGreedyPolicy): The policy to select actions.
            lr (float, optional): Learning rate. Defaults to 0.1.
            gamma (float, optional): Discount factor. Defaults to 0.9.
        """
        self.actions = actions
        self.policy = policy
        self.lr = max(lr, lr * 0.999)
        self.gamma = gamma

        self.q_table: QTable = QTable(actions.n)

    def choose_action(self, state: TrainStateType) -> int:
        """
        Chooses an action based on the current state using the defined policy.

        Args:
            state (StateType): Current environment state.

        Returns:
            int: Index of the selected action.
        """
        return self.policy.choose(self.q_table.get(state), self.actions)

    def learn(
        self,
        state: TrainStateType,
        action: int,
        reward: NumericType,
        next_state: TrainStateType,
    ) -> None:
        """
        Updates the Q-table based on the observed transition.

        Args:
            state: Previous state.
            action: Action taken.
            reward: Received reward.
            next_state: Next state after the action.
        """
        next_q_values = self.q_table.get(next_state)
        target = reward + self.gamma * np.max(next_q_values)
        self.q_table.update(state, action, target, self.lr)

    def decay_exploration(self) -> None:
        """
        Decays the epsilon value of the policy, reducing exploration over time.
        """
        self.policy.decay_epsilon()
