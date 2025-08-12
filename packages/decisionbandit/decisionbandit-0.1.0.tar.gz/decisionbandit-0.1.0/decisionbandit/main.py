# flake8: noqa

import numpy as np



def exploration(reward_prob,n_arms,t_steps):
    rewards = [[] for _ in range(n_arms)]
    for i in range(t_steps):
        arm = np.random.choice(n_arms)
        if np.random.rand() < reward_prob[arm]:
            rewards[arm].append(1)
        else:
            rewards[arm].append(0)
    return rewards


def exploit(reward_prob,n_arms,t_steps):
    rewards = [[] for _ in range(n_arms)]
    arm = np.random.choice(n_arms)
    for i in range(t_steps):
        if np.random.rand() < reward_prob[arm - 1]:
            rewards[arm].append(1)
        else:
            rewards[arm].append(0)
    return rewards


def fixed_exploration_then_exploitation(reward_prob,fixed,n_arms,t_steps):
    rewards = [[] for _ in range(n_arms)]
    for i in range(fixed):
        arm = np.random.choice(n_arms)
        if np.random.rand() < reward_prob[arm]:
            rewards[arm].append(1)
        else:
            rewards[arm].append(0)
    Q_explore = [[] for _ in range(n_arms)]
    for i in range(5):
        Q_explore[i] = np.sum(rewards[i]) / len(rewards[i])
    arm = np.argmax(Q_explore)
    print(f'Current Arm with Max reward is {arm} with Value {np.max(Q_explore)}')
    for i in range(t_steps - fixed):
        if np.random.rand() < reward_prob[arm]:
            rewards[arm].append(1)
        else:
            rewards[arm].append(0)
    Q_explore_exploit = [[] for _ in range(n_arms)]
    for i in range(n_arms):
        Q_explore_exploit[i] = np.sum(rewards[i]) / len(rewards[i])
    print(f'reward after exploitation for arm {np.argmax(Q_explore_exploit)} is {np.max(Q_explore_exploit)}')
    return Q_explore_exploit


def epsilon_greedy(reward_prob,epsilon, n_arms,t_steps):
    rewards = [[] for _ in range(n_arms)]
    Q_values = [0 for _ in range(n_arms)]
    for i in range(t_steps):
        if np.random.rand() < epsilon:
            arm = np.random.choice(n_arms)
        else:
            arm = np.argmax(Q_values)
        reward = 1 if np.random.rand() < reward_prob[arm] else 0
        rewards[arm].append(reward)
        Q_values[arm] = np.mean(rewards[arm])
    best_arm = np.argmax(Q_values)
    print(f'Final estimated rewards: {Q_values}')
    print(f'Best arm: {best_arm} with estimated reward: {np.max(Q_values)}')
    return (best_arm, Q_values)


def epsilon_greedy_with_ucb(reward_prob,epsilon,n_arms,t_steps, C_value):
    rewards = [[] for _ in range(n_arms)]
    Q_values = [0 for _ in range(n_arms)]
    counts = [0 for _ in range(n_arms)]
    for i in range(t_steps):
        if np.random.rand() < epsilon:
            ucb_values = []
            for j in range(n_arms):
                if counts[j] == 0:
                    ucb_values.append(float('inf'))
                else:
                    confidence = C_value * np.sqrt(np.log(i + 1) / counts[j])
                    ucb_values.append(Q_values[j] + confidence)
            arm = np.argmax(ucb_values)
        else:
            arm = np.argmax(Q_values)
        reward = 1 if np.random.rand() < reward_prob[arm] else 0
        rewards[arm].append(reward)
        counts[arm] += 1
        Q_values[arm] = np.mean(rewards[arm])
    best_arm = np.argmax(Q_values)
    print(f'Final Q-values: {Q_values}')
    print(f'Best arm: {best_arm} with estimated reward: {np.max(Q_values)}')
    return (best_arm, Q_values)
