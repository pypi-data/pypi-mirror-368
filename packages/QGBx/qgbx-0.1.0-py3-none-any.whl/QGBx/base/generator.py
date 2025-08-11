import pennylane as qml
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from .device import Device
from .distribution import Distribution
from ..distributions import *
import inspect
import os


class Generator:
    """
    Main class responsible for generating and executing Galton Board quantum circuits.
    """

    def __init__(
        self,
        device: Device,
        distribution: Distribution,
        
    ):
        """
        Initialize the generator with a quantum device and a probability distribution.

        Args:
            device (Device): Quantum device instance.
            distribution (Distribution): Distribution instance for the Galton Board.
            
        """
        self.device = device
        self.n_layers = 0
        self.gb = None
        self.measure_wires = None
        self.crct_args = None

        

        if distribution.name not in [
            "Gaussian",
            "Exponential",
            "Hadamard_QW",
            "Layer_Controlled",
            "Peg_Controlled"
        ]:
            raise Exception("Distribution not recognized.")
        else:
            self.dist = distribution

    def galton_board(self, n_layers):
        """
        Build the Galton Board circuit.

        Args:
            n_layers (int): Number of layers in the Galton Board.

        Returns:
            Quantum circuit object.
        """
        self.n_layers = n_layers
        self.gb, self.measure_wires, self.crct_args = self.dist.circuit(n_layers)
        self.device.circuit = self.gb
        return self.gb

    def run(self):
        """
        Execute the Galton Board circuit on the configured device.

        Returns:
            dict: One-hot probability distribution from execution.
        """
        if self.gb is None:
            raise Exception("Galton Board not yet created.")

        if self.device.device_name == "IBM_Torino":
            job = self.device.run_circuit()
            return job
        else:
            results = self.device.run_circuit(measure_wires=self.measure_wires)
            self.dist.probs = results
            self.dist.ideal_dist = self.dist.ideal_distribution(**self.crct_args)
            return results

    def job_results(self, jobID):
        """
        Retrieve results for a given IBM job ID.

        Args:
            jobID (str): IBM Quantum job ID.

        Returns:
            dict: One-hot probability distribution.
        """
        if self.device.device_name == "IBM_Torino":
            results = self.device.job_results(self.measure_wires, jobID)
            self.dist.probs = results
            self.dist.ideal_dist = self.dist.ideal_distribution(**self.crct_args)
            return results

    def export_circuit_as_png(self, fold=-1, filename="circuit.png", style="black_white"):
        """
        Export the circuit diagram as a PNG image.

        Args:
            fold (int): Folding parameter for circuit visualization.
            filename (str): Output filename.
            style (str): Diagram style.
        """
        if not filename.lower().endswith(".png"):
            filename += ".png"

        try:
            fig = self.device.draw_circuit(fold=fold)
            fig.savefig(filename)
        except Exception as e:
            print("Failed to export circuit diagram:", e)

    def draw_circuit(self, fold=-1):
        """
        Draw the circuit using the device's visualization method.

        Args:
            fold (int): Folding parameter for circuit visualization.
        """
        self.device.draw_circuit(fold=fold)

    def export_qasm(self, version="2", filename="exported_circuit.txt"):
        """
        Export the circuit as a QASM file.

        Args:
            version (str): QASM version.
            filename (str): Output filename.
        """
        if not filename.lower().endswith(".txt"):
            filename += ".txt"

        if self.device.device_name in ["Qiskit_AerSimulator", "Qiskit_FakeTorino", "IBM_Torino"]:
            self.device.export_qasm(version, filename=filename)
        else:
            raise Exception("This circuit cannot be exported as a QASM file.")
