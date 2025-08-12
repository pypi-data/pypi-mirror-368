import matplotlib.pyplot as plt

def plot_reward_vs_steps(steps, rewards, window=10, title="Rewards vs Steps"):
    """
    Plots rewards against steps with optional moving average smoothing.

    Args:
        steps (list or array): List of step counts (x-axis).
        rewards (list or array): List of rewards at each step (y-axis).
        window (int): Window size for moving average smoothing.
        title (str): Plot title.
    """
    plt.figure(figsize=(8, 5))
    plt.plot(steps, rewards, label="Reward", alpha=0.6)

    if window > 1 and len(rewards) >= window:
        moving_avg = [
            sum(rewards[i-window:i]) / window
            for i in range(window, len(rewards) + 1)
        ]
        plt.plot(steps[window - 1:], moving_avg,
                 label=f"{window}-Step Moving Avg", color="red", linewidth=2)

    plt.xlabel("Steps")
    plt.ylabel("Reward")
    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.show()
