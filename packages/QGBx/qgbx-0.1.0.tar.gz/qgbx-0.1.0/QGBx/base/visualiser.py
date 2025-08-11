import matplotlib.pyplot as plt
import numpy as np
from .distribution import Distribution


class Visualiser:
    """
    Handles visualization of probability distributions for the Quantum Galton Board.
    """

    def __init__(self, distribution: Distribution):
        """
        Initialize the visualizer.

        Args:
            distribution (Distribution): The distribution object to visualize.
        """
        self.probs = distribution.probs
        self.idl = distribution.ideal_dist
        self.dist_name = distribution.name
        

    def plot(self, interval_length=None, ideal=False):
        """
        Plot the probability distribution.

        Args:
            interval_length (int, optional): Number of bins to display.
            ideal (bool): Whether to plot the ideal distribution instead of measured.
        """
        if not ideal:
            distribution = self.probs
            
            title = f"{self.dist_name} Probability Distribution using the Quantum Galton Board"
        else:
            distribution = self.idl
            
            title = f"The Ideal {self.dist_name} Probability Distribution"

        original_values = list(distribution.values())
        n = len(original_values)

        if interval_length is None:
            interval_length = n

        center = n // 2
        start = center - interval_length // 2
        end = start + interval_length

        if interval_length > n:
            pad_left = max(0, -start)
            pad_right = max(0, end - n)
            padded_values = [0] * pad_left + original_values + [0] * pad_right
            start = max(0, start)
            values = padded_values[start:start + interval_length]
        else:
            start = max(0, start)
            end = min(n, end)
            values = original_values[start:end]

        labels = list(range(start, start + len(values)))

        plt.style.use('seaborn-v0_8')
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

        # Light blue gradient background
        gradient = np.linspace(0, 1, 256).reshape(1, -1)
        gradient = np.vstack((gradient, gradient))
        ax.imshow(
            gradient,
            aspect='auto',
            cmap='Blues',
            alpha=0.1,
            extent=[-0.5, len(values) - 0.5, 0, max(values) * 1.2]
        )

        ax.bar([str(label) for label in labels], values, color='blue', edgecolor='navy', linewidth=0.8, alpha=0.9)

        ax.set_xlabel("Bin", fontsize=12, fontweight='bold', color='navy')
        ax.set_ylabel("Probability", fontsize=12, fontweight='bold', color='navy')
        ax.set_title(title, fontsize=16, fontweight='bold', color='darkblue', pad=20)

        ax.grid(axis='y', linestyle='--', alpha=0.4, color='gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('navy')
        ax.spines['bottom'].set_color('navy')

        plt.tight_layout()
        plt.show()

    def plot_with_ideal(self, interval_length=None):
        """
        Plot the measured probability distribution with the ideal distribution overlaid.

        Args:
            interval_length (int, optional): Number of bins to display.
        """
        probs = self.probs
        idl = self.idl

        title = f"{self.dist_name} Probability Distribution with Ideal Overlay"

        original_values = list(probs.values())
        ideal_values = list(idl.values())
        n = len(original_values)

        if interval_length is None:
            interval_length = n

        center = n // 2
        start = center - interval_length // 2
        end = start + interval_length

        if interval_length > n:
            pad_left = max(0, -start)
            pad_right = max(0, end - n)
            padded_values = [0] * pad_left + original_values + [0] * pad_right
            padded_ideal = [0] * pad_left + ideal_values + [0] * pad_right
            start = max(0, start)
            values = padded_values[start:start + interval_length]
            ideal_vals = padded_ideal[start:start + interval_length]
        else:
            start = max(0, start)
            end = min(n, end)
            values = original_values[start:end]
            ideal_vals = ideal_values[start:end]

        labels = list(range(start, start + len(values)))

        plt.style.use('seaborn-v0_8')
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

        # Background gradient
        gradient = np.linspace(0, 1, 256).reshape(1, -1)
        gradient = np.vstack((gradient, gradient))
        ax.imshow(
            gradient,
            aspect='auto',
            cmap='Blues',
            alpha=0.1,
            extent=[-0.5, len(values) - 0.5, 0, max(values + ideal_vals) * 1.2]
        )

        ax.bar(
            [str(label) for label in labels],
            values,
            color='blue',
            edgecolor='navy',
            linewidth=0.8,
            alpha=0.9,
            label="Non-ideal (measured)"
        )

        ax.plot(
            [str(label) for label in labels],
            ideal_vals,
            color='red',
            marker='o',
            linestyle='-',
            linewidth=1.5,
            markersize=6,
            label="Ideal"
        )

        ax.set_xlabel("Bin", fontsize=12, fontweight='bold', color='navy')
        ax.set_ylabel("Probability", fontsize=12, fontweight='bold', color='navy')
        ax.set_title(title, fontsize=16, fontweight='bold', color='darkblue', pad=20)

        ax.grid(axis='y', linestyle='--', alpha=0.4, color='gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('navy')
        ax.spines['bottom'].set_color('navy')

        ax.legend()

        plt.tight_layout()
        plt.show()
