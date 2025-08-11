from ...base.distribution import Distribution
from ...base.device import Device
import pennylane as qml
import numpy as np
from ...utils import rx_angles_from_probabilities, cos_angles_from_probabilities
from qiskit import QuantumCircuit
from math import comb


class GaussianOp(Distribution):
    """
    Optimized Gaussian distribution generator for the Quantum Galton Board.
    """

    def __init__(self, device, p=0.5, RBS=1, **kwargs):
        super().__init__(device, "Gaussian", **kwargs)
        self.number_of_layers = 0
        self.p = p
        self.RBS = RBS

    def circuit(self, n_layers):
        """
        Build the Gaussian quantum circuit.
        
        Args:
            n_layers (int): Number of layers in the Galton Board.
        """
        self.number_of_layers = n_layers
        num_qubits = n_layers + 1
        ball_qubit = n_layers - 1
        ball_measure_wires = [ball_qubit + i for i in range(-n_layers, n_layers + 1, 2)]
        kwargs_dict = {"interval_size": len(ball_measure_wires), "p": self.p}

        angle_up = rx_angles_from_probabilities(self.p).item()
        angle_down = cos_angles_from_probabilities(1 - self.p).item()
        ancilla = n_layers + 1

        if self.device_name == "Pennylane_default.qubit":
            pass

        elif self.device_name in ["Qiskit_AerSimulator", "Qiskit_FakeTorino", "IBM_Torino"]:

            def add_beamsplitter(qc: QuantumCircuit, ctrl: int, tgt: int, theta: float):
                if self.RBS == 1:
                    qc.cx(tgt, ctrl)
                    qc.cry(theta, ctrl, tgt)
                    qc.cx(tgt, ctrl)
                elif self.RBS == 2:
                    qc.h(tgt)
                    qc.cx(tgt, ctrl)
                    qc.ry(theta / 2, tgt)
                    qc.ry(theta / 2, ctrl)
                    qc.cx(tgt, ctrl)
                    qc.h(tgt)
                else:
                    raise Exception("Reconfigured beamsplitter type unknown")

            def add_beamsplitter_i(qc: QuantumCircuit, ctrl: int, tgt: int, theta: float, ancilla_qubit: int):
                if self.RBS == 1:
                    qc.cx(ctrl, ancilla_qubit)
                    qc.cry(theta, ancilla_qubit, ctrl)
                    qc.cx(ctrl, ancilla_qubit)
                    qc.cx(ancilla_qubit, tgt)
                    qc.reset(ancilla_qubit)
                elif self.RBS == 2:
                    qc.h(ctrl)
                    qc.cx(ctrl, ancilla_qubit)
                    qc.ry(theta / 2, ctrl)
                    qc.ry(theta / 2, ancilla_qubit)
                    qc.cx(ctrl, ancilla_qubit)
                    qc.h(ctrl)
                    qc.cx(ancilla_qubit, tgt)
                    qc.reset(ancilla_qubit)
                else:
                    raise Exception("Reconfigured beamsplitter type unknown")

            def gaussian_circuit():
                qc = QuantumCircuit(n_layers + 2, n_layers + 1)
                qc.x(ball_qubit)

                for layer in range(n_layers):
                    for i in range(layer + 1):
                        if layer == 0:
                            add_beamsplitter(qc, ball_qubit + 1, ball_qubit, angle_up)
                        else:
                            if i == 0:
                                add_beamsplitter(qc, ball_qubit - layer, ball_qubit - layer + 1, angle_down)
                            else:
                                ctrl = ball_qubit - layer + i
                                tgt = ctrl + 1
                                add_beamsplitter_i(qc, tgt, ctrl, angle_down, ancilla)
                    qc.barrier()

                qc.measure(range(num_qubits), range(num_qubits))
                return qc

            return gaussian_circuit, ball_measure_wires, kwargs_dict

    def ideal_distribution(self, **kwargs):
        """
        Compute the ideal Gaussian (binomial) distribution.
        
        Args:
            interval_size (int): Number of bins in the distribution (required).
            p (float): Probability of success (default: 0.5).
        """
        n = kwargs["interval_size"] - 1
        p = kwargs.get("p", 0.5)
        probs = np.array([comb(n, k) * (p ** k) * ((1 - p) ** (n - k)) for k in range(n + 1)])
        probs /= np.sum(probs)
        self.ideal_dist = {i: float(prob) for i, prob in enumerate(probs)}
        return self.ideal_dist
