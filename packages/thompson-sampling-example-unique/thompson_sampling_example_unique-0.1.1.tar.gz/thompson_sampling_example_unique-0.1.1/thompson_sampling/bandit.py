
# thompson_sampling/bandit.py

import numpy as np

class ThompsonSampling:
    """
    A class implementing Thompson Sampling for the Multi-Armed Bandit problem.

    Attributes
    ----------
    n_arms : int
        Number of arms (options) in the bandit.
    successes : np.ndarray
        Counts of observed successes for each arm.
    failures : np.ndarray
        Counts of observed failures for each arm.

    Methods
    -------
    select_arm():
        Selects an arm based on Thompson Sampling.
    update(arm, reward):
        Updates the success/failure count based on the observed reward.
    """

    def __init__(self, n_arms: int):
        """
        Parameters
        ----------
        n_arms : int
            Number of arms (options) in the bandit.
        """
        self.n_arms = n_arms
        self.successes = np.zeros(n_arms)
        self.failures = np.zeros(n_arms)

    def select_arm(self) -> int:
        """
        Select an arm using Thompson Sampling.

        Returns
        -------
        int
            Index of the selected arm.
        """
        samples = [
            np.random.beta(self.successes[i] + 1, self.failures[i] + 1)
            for i in range(self.n_arms)
        ]
        return int(np.argmax(samples))

    def update(self, arm: int, reward: int):
        """
        Update the counts of successes and failures for the given arm.

        Parameters
        ----------
        arm : int
            The index of the arm that was pulled.
        reward : int
            Reward received from pulling the arm (1 for success, 0 for failure).
        """
        if reward == 1:
            self.successes[arm] += 1
        else:
            self.failures[arm] += 1
