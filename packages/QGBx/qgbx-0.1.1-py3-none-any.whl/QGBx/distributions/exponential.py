from ..base.distribution import Distribution
from ..base.device import Device
import pennylane as qml
import numpy as np
from ..utils import *
from qiskit import QuantumCircuit


class Exponential(Distribution):
    """
    Exponential distribution generator for the Quantum Galton Board.

    This class builds a quantum circuit that simulates an exponential 
    probability distribution using the Galton board approach.
    """

    def __init__(self, device, rate=1, reversed=False, **kwargs):
        """
        Initialize the Exponential distribution.

        Args:
            device: Quantum device instance.
            rate (float): Decay rate of the distribution.
            reversed (bool): If True, distribution decays to the left.
        """
        super().__init__(device, name = "Exponential", **kwargs)
        self.rate = rate
        self.reversed = reversed

    def circuit(self, n_layers):
        """
        Create the quantum circuit for the Exponential distribution.

        Args:
            n_layers (int): Number of Galton board layers.

        Returns:
            tuple: (Circuit function/Qiskit circuit, measurement wires, kwargs_dict)
        """
        self.number_of_layers = n_layers
        num_qubits = 2 * (n_layers + 1)
        control_qubit = 0
        ball_qubit = n_layers + 1

        ball_measure_wires = [ball_qubit + i for i in range(-n_layers, n_layers + 1, 2)]
        L = len(ball_measure_wires)

        target_exponential = list(
            self.ideal_distribution(
                interval_size=L, rate=self.rate, reverse=self.reversed
            ).values()
        )

        res = solve_per_peg(N=L - 1, target=target_exponential)
        if res.success:
            x = res.x
            offsets = flatten_indices(L)
            flat_probs = []
            for i in range(L):
                row_p = x[offsets[i]:offsets[i] + (i + 1)]
                flat_probs.extend(row_p[::-1])  # reverse each row
            probs = flat_probs
        else:
            raise RuntimeError(f"Solver failed: {res.message}")

        angles = rx_angles_from_probabilities(probs).tolist()
        kwargs_dict = {"interval_size": L, "rate": self.rate, "reverse": self.reversed}

        # --- Pennylane implementation ---
        if self.device_name == "Pennylane_default.qubit":

            def peg(i):
                qml.CSWAP(wires=[control_qubit, i, i - 1])
                qml.CNOT(wires=[i, control_qubit])
                qml.CSWAP(wires=[control_qubit, i, i + 1])

            def peg_i(i, angle):
                m = qml.measure(wires=control_qubit)
                qml.cond(m, qml.PauliX)(wires=control_qubit)
                qml.RX(angle, wires=control_qubit)
                qml.CSWAP(wires=[control_qubit, i, i - 1])
                qml.CNOT(wires=[i, control_qubit])
                qml.CSWAP(wires=[control_qubit, i, i + 1])

            @qml.qnode(self.dev(wires=num_qubits))
            def ExponentialCircuit():
                cnt = 0
                qml.RX(angles[cnt], wires=control_qubit)
                cnt += 1
                qml.PauliX(wires=ball_qubit)

                for layer in range(n_layers):
                    positions = [
                        ball_qubit + pos
                        for pos in range(-layer, layer + 1, 2)
                        if 0 < ball_qubit + pos < num_qubits - 1
                    ]
                    for i in positions:
                        if layer == 0:
                            peg(i)
                        else:
                            peg_i(i, angles[cnt])
                            cnt += 1

                return qml.sample(wires=ball_measure_wires)

            return ExponentialCircuit, ball_measure_wires, kwargs_dict

        # --- Qiskit implementation ---
        elif self.device_name in ["Qiskit_AerSimulator", "Qiskit_FakeTorino", "IBM_Torino"]:

            def peg(qc, i, ctrl):
                qc.cswap(ctrl, i, i - 1)
                qc.cx(i, ctrl)
                qc.cswap(ctrl, i, i + 1)

            def peg_i(qc, i, ctrl, angle):
                qc.reset(ctrl)
                qc.rx(angle, ctrl)
                qc.cswap(ctrl, i, i - 1)
                qc.cx(i, ctrl)
                qc.cswap(ctrl, i, i + 1)

            def ExponentialCircuit():
                qc = QuantumCircuit(num_qubits, len(ball_measure_wires))
                cnt = 0

                qc.rx(angles[cnt], control_qubit)
                cnt += 1
                qc.x(ball_qubit)

                for layer in range(n_layers):
                    positions = [
                        ball_qubit + pos
                        for pos in range(-layer, layer + 1, 2)
                        if 0 < ball_qubit + pos < num_qubits - 1
                    ]
                    for i in positions:
                        if layer == 0:
                            peg(qc, i, control_qubit)
                        else:
                            peg_i(qc, i, control_qubit, angles[cnt])
                            cnt += 1

                    if layer < n_layers:
                        for j, i in enumerate(positions):
                            if j < len(positions) - 1:
                                qc.cx(i + 2, i + 1)
                                qc.reset(i + 2)

                qc.barrier()
                for idx, wire in enumerate(ball_measure_wires):
                    qc.measure(wire, idx)

                return qc

            return ExponentialCircuit, ball_measure_wires, kwargs_dict

    def ideal_distribution(self, **kwargs):
        """
        Compute the ideal exponential probability distribution.

        Args:
            interval_size (int): Number of bins in the distribution.
            rate (float): Decay rate of the exponential.
            reverse (bool): If True, reverse the distribution.

        Returns:
            dict: Mapping index -> probability.
        """
        n = kwargs["interval_size"]
        rate = kwargs.get("rate", 1.0)
        reverse = kwargs.get("reverse", False)

        probs = rate * np.exp(-rate * np.arange(n))
        if reverse:
            probs = probs[::-1]
        probs /= np.sum(probs)

        dict_probs = {i: float(prob) for i, prob in enumerate(probs)}
        self.ideal_dist = dict_probs
        return dict_probs
