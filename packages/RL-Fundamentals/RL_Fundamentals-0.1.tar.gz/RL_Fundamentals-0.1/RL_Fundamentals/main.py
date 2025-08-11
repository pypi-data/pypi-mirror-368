import numpy as np
def ucb_strategy(trials, arms, prob_win_eacharm):
    Q = np.zeros(arms)  # Estimated rewards for each arm
    N = np.zeros(arms)  # Number of times each arm has been pulled
    rewards = []
    cumulative_rewards = np.zeros(trials)  # To store cumulative rewards for plotting

    for t in range(1, trials + 1):  # Start from trial 1
        if t <= arms:  # Pull each arm at least once in the first `arms` trials
            chosen_arm = t - 1
        else:
            ucb_values = Q + np.sqrt(2 * np.log(t) / (N + 1e-5))  # Avoid division by zero
            chosen_arm = np.argmax(ucb_values)

        # Simulate the reward for the chosen arm
        reward = 1 if np.random.rand() < prob_win_eacharm[chosen_arm] else 0
        rewards.append(reward)

        # Update estimated rewards and counts
        N[chosen_arm] += 1
        Q[chosen_arm] += (reward - Q[chosen_arm]) / N[chosen_arm]

        # Track cumulative rewards
        cumulative_rewards[t-1] = cumulative_rewards[t-2] + reward if t > 1 else reward

    print("Estimated rewards:", Q)
    print("Total reward:", sum(rewards))
    return rewards, cumulative_rewards, Q