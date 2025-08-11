import numpy as np
import matplotlib.pyplot as plt
from .distribution import Distribution


class Analyzer:
    def __init__(self, distribution: Distribution):
        self.distribution = distribution

        if distribution.ideal_dist is None:
            raise ValueError("The ideal distribution is not yet computed.")
        else:
            self.ideal = self._dict_to_array(distribution.ideal_dist)

        if distribution.probs is None:
            raise ValueError("The Quantum Galton Board distribution is not yet generated.")
        else:
            self.quantum = self._dict_to_array(distribution.probs)

        if len(self.ideal) != len(self.quantum):
            raise ValueError("Distributions must have the same number of bins.")

    def _dict_to_array(self, dist_dict):
        """Convert a dict with sorted keys to a numpy array of probabilities."""
        return np.array([dist_dict[k] for k in sorted(dist_dict.keys())])

    def total_variation_distance(self):
        """Calculate total variation distance between ideal and quantum distributions."""
        value = 0.5 * np.sum(np.abs(self.ideal - self.quantum))
        threshold = 0.02
        passed = value <= threshold
        interpretation = "Closer to 0 means distributions are nearly identical."
        return {
            "Distribution": self.distribution.name,
            "Test": "Total Variation Distance",
            "Result": float(value),
            "Passed": passed,
            "Interpretation": interpretation,
            "Tolerance": threshold
        }

    def jensen_shannon_divergence(self):
        """Calculate Jensen-Shannon divergence between ideal and quantum distributions."""
        M = 0.5 * (self.ideal + self.quantum)
        kl1 = np.sum(self.ideal * np.log((self.ideal + 1e-12) / (M + 1e-12)))
        kl2 = np.sum(self.quantum * np.log((self.quantum + 1e-12) / (M + 1e-12)))
        value = 0.5 * (kl1 + kl2)
        threshold = 0.05
        passed = value <= threshold
        interpretation = "Smaller values indicate higher similarity (0 = perfect match)."
        return {
            "Distribution": self.distribution.name,
            "Test": "Jensen-Shannon Divergence",
            "Result": float(value),
            "Passed": passed,
            "Interpretation": interpretation,
            "Tolerance": threshold
        }

    def chi_squared_test(self):
        """Calculate Chi-Squared statistic between observed and expected distributions."""
        expected = self.ideal
        observed = self.quantum
        value = np.sum((observed - expected) ** 2 / (expected + 1e-12))
        threshold = 0.1  # Threshold depends on degrees of freedom
        passed = value <= threshold
        interpretation = "Low χ² value means observed ≈ expected."
        return {
            "Distribution": self.distribution.name,
            "Test": "Chi-Squared Statistic",
            "Result": float(value),
            "Passed": passed,
            "Interpretation": interpretation,
            "Tolerance": threshold
        }

    def hellinger_distance(self):
        """Calculate Hellinger distance between ideal and quantum distributions."""
        value = (1 / np.sqrt(2)) * np.linalg.norm(np.sqrt(self.ideal) - np.sqrt(self.quantum))
        threshold = 0.1
        passed = value <= threshold
        interpretation = "0 = perfect similarity; values < 0.1 are generally acceptable."
        return {
            "Distribution": self.distribution.name,
            "Test": "Hellinger Distance",
            "Result": float(value),
            "Passed": passed,
            "Interpretation": interpretation,
            "Tolerance": threshold
        }

    def entropy_difference(self):
        """Calculate absolute difference in entropy between ideal and quantum distributions."""
        def entropy(p):
            p = p[p > 0]
            return -np.sum(p * np.log(p))

        value = abs(entropy(self.ideal) - entropy(self.quantum))
        threshold = 0.05
        passed = value <= threshold
        interpretation = "Smaller difference means similar randomness/uncertainty."
        return {
            "Distribution": self.distribution.name,
            "Test": "Entropy Difference",
            "Result": float(value),
            "Passed": passed,
            "Interpretation": interpretation,
            "Tolerance": threshold
        }

    def analyze(self, thresholds=None, show_passed=False):
        """
        Run all analysis tests and display results in a formatted matplotlib table.

        Parameters:
            thresholds (dict): Optional custom thresholds for each metric.
                            Keys should match test function names:
                            {
                                "total_variation_distance": 0.02,
                                "jensen_shannon_divergence": 0.05,
                                "chi_squared_test": 0.1,
                                "hellinger_distance": 0.1,
                                "entropy_difference": 0.05
                            }
            show_passed (bool): Whether to display the "Passed" column in the table.
        """
        # Default thresholds
        default_thresholds = {
            "total_variation_distance": 0.02,
            "jensen_shannon_divergence": 0.05,
            "chi_squared_test": 0.1,
            "hellinger_distance": 0.1,
            "entropy_difference": 0.05
        }
        [0.02,0.05,0.1,0.1,0.05]
        if thresholds:
            default_thresholds.update(thresholds)

        # Run tests with updated thresholds
        self.results = [
            self.total_variation_distance(),
            self.jensen_shannon_divergence(),
            self.chi_squared_test(),
            self.hellinger_distance(),
            self.entropy_difference()
        ]

        # Update results with custom thresholds and pass/fail status
        for res in self.results:
            func_name = res["Test"].lower().replace(" ", "_")
            if func_name in default_thresholds:
                res["Tolerance"] = default_thresholds[func_name]
                res["Passed"] = res["Result"] <= default_thresholds[func_name]

        # Prepare table headers
        headers = ["Test Name", "Result", "Interpretation"]
        if show_passed:
            headers.insert(2, "Passed")
            headers.append("Tolerance")

        # Prepare table data
        cell_data = []
        for row in self.results:
            row_fmt = row.copy()
            row_fmt["Passed"] = "Yes" if row["Passed"] else "No"
            table_row = [
                row_fmt["Test"],
                round(row_fmt["Result"], 4),
                row_fmt["Interpretation"]
            ]
            if show_passed:
                table_row.insert(2, row_fmt["Passed"])
                table_row.append(row_fmt["Tolerance"])
            cell_data.append(table_row)

        # Display table
        fig, ax = plt.subplots(figsize=(12, 2 + len(self.results) * 0.5))
        ax.axis("off")

        table = ax.table(
            cellText=cell_data,
            colLabels=headers,
            loc="center",
            cellLoc="center",
            colColours=["lightgray"] * len(headers)
        )

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.2)

        ax.set_title(
            f'{self.distribution.name} Distribution Simulation Analysis',
            fontsize=16,
            fontweight="bold",
            pad=-20
        )
        plt.show()

    def get_analyze_results(self):
        """
        Return analysis results as a dictionary:
        { "Test Name": result_value }
        """
        if not hasattr(self, "results"):
            self.analyze(show_passed=False)  # Run analysis if not yet done
        return {res["Test"]: res["Result"] for res in self.results}
