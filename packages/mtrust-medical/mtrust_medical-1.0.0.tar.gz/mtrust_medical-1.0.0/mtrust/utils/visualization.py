"""
Visualization utilities for M-TRUST.
Provides simple plotting and explainability helpers.
"""

import matplotlib.pyplot as plt
import numpy as np

class Visualization:
    @staticmethod
    def plot_fairness_metrics(metrics_dict):
        """
        Plots fairness metrics as a bar chart.

        Args:
            metrics_dict (dict): {metric_name: value}
        """
        names = list(metrics_dict.keys())
        values = [metrics_dict[k] for k in names]

        plt.figure(figsize=(6, 4))
        bars = plt.bar(names, values, color='skyblue')
        plt.ylim(0, 1)
        plt.ylabel("Score")
        plt.title("Fairness Metrics")
        plt.xticks(rotation=45)

        # Label each bar
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, value + 0.02,
                     f"{value:.2f}", ha='center')

        plt.tight_layout()
        plt.show()

    @staticmethod
    def show_saliency_map(image, saliency):
        """
        Displays an image with an overlayed saliency heatmap.

        Args:
            image (np.ndarray): Original grayscale or RGB image.
            saliency (np.ndarray): Saliency map (same size as image).
        """
        plt.figure(figsize=(6, 6))
        plt.imshow(image, cmap='gray')
        plt.imshow(saliency, cmap='jet', alpha=0.5)
        plt.axis('off')
        plt.title("Saliency Map")
        plt.show()
