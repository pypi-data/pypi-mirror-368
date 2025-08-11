import numpy as np

class SimpleMDP:
    """
    A simple Markov Decision Process.
    """

    def __init__(self, num_states, num_actions, transition_probabilities, rewards):
        """
        Initializes the SimpleMDP.

        Args:
            num_states: The number of states in the MDP.
            num_actions: The number of actions in the MDP.
            transition_probabilities: A numpy array of shape (num_states, num_actions, num_states)
                                     representing the probability of transitioning from state s to s'
                                     when taking action a in state s.
            rewards: A numpy array of shape (num_states, num_actions, num_states)
                     representing the reward received when transitioning from state s to s'
                     when taking action a in state s.
        """
        self.num_states = num_states
        self.num_actions = num_actions
        self.transition_probabilities = transition_probabilities
        self.rewards = rewards

    def calculate_expected_value(self, policy, gamma=0.99):
        """
        Calculates the expected value of each state given a policy.

        Args:
            policy: A numpy array of shape (num_states,) representing the action taken in each state.
            gamma: The discount factor.

        Returns:
            A numpy array of shape (num_states,) representing the value of each state.
        """
        # Initialize value function
        V = np.zeros(self.num_states)

        # Iterate until convergence
        while True:
            V_prev = V.copy()
            for s in range(self.num_states):
                a = policy[s]
                V[s] = np.sum([self.transition_probabilities[s, a, s_prime] * (self.rewards[s, a, s_prime] + gamma * V_prev[s_prime]) for s_prime in range(self.num_states)])

            if np.allclose(V, V_prev):
                break
        return V

    def value_iteration(self, gamma=0.99, theta=1e-9):
        """
        Performs value iteration to find the optimal value function and policy.

        Args:
            gamma: The discount factor.
            theta: The convergence threshold.

        Returns:
            A tuple containing:
                - A numpy array of shape (num_states,) representing the optimal value function.
                - A numpy array of shape (num_states,) representing the optimal policy.
        """
        V = np.zeros(self.num_states)
        while True:
            delta = 0
            for s in range(self.num_states):
                v = V[s]
                V[s] = np.max([np.sum([self.transition_probabilities[s, a, s_prime] * (self.rewards[s, a, s_prime] + gamma * V[s_prime]) for s_prime in range(self.num_states)]) for a in range(self.num_actions)])
                delta = max(delta, abs(v - V[s]))
            if delta < theta:
                break

        policy = np.zeros(self.num_states, dtype=int)
        for s in range(self.num_states):
            policy[s] = np.argmax([np.sum([self.transition_probabilities[s, a, s_prime] * (self.rewards[s, a, s_prime] + gamma * V[s_prime]) for s_prime in range(self.num_states)]) for a in range(self.num_actions)])

        return V, policy

    def policy_iteration(self, gamma=0.99):
        """
        Performs policy iteration to find the optimal value function and policy.

        Args:
            gamma: The discount factor.

        Returns:
            A tuple containing:
                - A numpy array of shape (num_states,) representing the optimal value function.
                - A numpy array of shape (num_states,) representing the optimal policy.
        """
        policy = np.random.randint(0, self.num_actions, self.num_states)

        while True:
            V = self.calculate_expected_value(policy, gamma)
            policy_stable = True
            for s in range(self.num_states):
                old_action = policy[s]
                policy[s] = np.argmax([np.sum([self.transition_probabilities[s, a, s_prime] * (self.rewards[s, a, s_prime] + gamma * V[s_prime]) for s_prime in range(self.num_states)]) for a in range(self.num_actions)])
                if old_action != policy[s]:
                    policy_stable = False
            if policy_stable:
                break
        return V, policy