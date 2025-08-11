from ..base.distribution import Distribution
import pennylane as qml
import numpy as np
from ..utils import rx_angles_from_probabilities
from qiskit import QuantumCircuit
from math import comb


class Gaussian(Distribution):
    """
    Gaussian-like (binomial) distribution implemented using a quantum Galton board.
    """

    def __init__(self, device, p=0.5, **kwargs):
        super().__init__(device, "Gaussian", **kwargs)
        self.number_of_layers = 0
        self.p = p

    def circuit(self, n_layers):
        """
        Build the Gaussian quantum Galton board circuit.

        Args:
            n_layers (int): Number of layers.

        Returns:
            tuple: (Circuit, measurement wires, kwargs for ideal distribution)
        """
        self.number_of_layers = n_layers
        num_qubits = 2 * (n_layers + 1)
        control_qubit = 0
        ball_qubit = n_layers + 1
        ball_measure_wires = [ball_qubit + i for i in range(-n_layers, n_layers + 1, 2)]

        kwargs_dict = {"interval_size": len(ball_measure_wires), "p": self.p}

        if self.device_name == "Pennylane_default.qubit":

            def peg(i):
                qml.CSWAP(wires=[control_qubit, i, i - 1])
                qml.CNOT(wires=[i, control_qubit])
                qml.CSWAP(wires=[control_qubit, i, i + 1])

            @qml.qnode(self.dev(wires=num_qubits))
            def gaussian_circuit():
                angle = rx_angles_from_probabilities(self.p).item()
                qml.RX(angle, wires=control_qubit)
                qml.PauliX(wires=ball_qubit)

                for layer in range(n_layers):
                    offset = layer
                    positions = [
                        ball_qubit + pos
                        for pos in range(-offset, offset + 1, 2)
                        if 0 < ball_qubit + pos < num_qubits - 1
                    ]

                    for j, i in enumerate(positions):
                        peg(i)
                        if j < len(positions) - 1:
                            qml.CNOT(wires=[i + 1, control_qubit])

                    if layer < n_layers - 1:
                        m = qml.measure(wires=control_qubit)
                        qml.cond(m, qml.PauliX)(wires=control_qubit)
                        qml.RX(angle, wires=control_qubit)

                return qml.sample(wires=ball_measure_wires)

            return gaussian_circuit, ball_measure_wires, kwargs_dict

        elif self.device_name in ["Qiskit_AerSimulator", "Qiskit_FakeTorino", "IBM_Torino"]:

            def peg(qc, i, ctrl):
                qc.cswap(ctrl, i, i - 1)
                qc.cx(i, ctrl)
                qc.cswap(ctrl, i, i + 1)

            def gaussian_circuit():
                qc = QuantumCircuit(num_qubits, len(ball_measure_wires))
                angle = rx_angles_from_probabilities(self.p).item()
                qc.rx(angle, control_qubit)
                qc.x(ball_qubit)

                for layer in range(n_layers):
                    offset = layer
                    positions = [
                        ball_qubit + pos
                        for pos in range(-offset, offset + 1, 2)
                        if 0 < ball_qubit + pos < num_qubits - 1
                    ]

                    for j, i in enumerate(positions):
                        peg(qc, i, control_qubit)
                        if j < len(positions) - 1:
                            qc.cx(i + 1, control_qubit)

                    if layer < n_layers - 1:
                        qc.reset(control_qubit)
                        qc.rx(angle, control_qubit)

                qc.barrier()
                for idx, wire in enumerate(ball_measure_wires):
                    qc.measure(wire, idx)

                return qc

            return gaussian_circuit, ball_measure_wires, kwargs_dict

    def ideal_distribution(self, **kwargs):
        """
        Returns a discrete binomial distribution as an index-to-probability dictionary.

        Parameters (via kwargs):
            - interval_size (int): Number of bins.
            - p (float): Probability of "success" (default: 0.5)
        """
        n = kwargs["interval_size"] - 1
        p = kwargs.get("p", 0.5)
        probs = np.array([comb(n, k) * (p ** k) * ((1 - p) ** (n - k)) for k in range(n + 1)])
        probs /= np.sum(probs)
        dict_probs = {i: float(prob) for i, prob in enumerate(probs)}
        self.ideal_dist = dict_probs
        return dict_probs
