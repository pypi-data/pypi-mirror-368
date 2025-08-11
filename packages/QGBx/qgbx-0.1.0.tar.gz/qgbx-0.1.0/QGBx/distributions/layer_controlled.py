from ..base.distribution import Distribution
from ..base.device import Device
import pennylane as qml
import numpy as np
from ..utils import (
    probabilities_from_rx_angles,
    rx_angles_from_probabilities,
    solve_galton_layer,
    galton_bin_probs_layer
)
from qiskit import QuantumCircuit


class LayerControlled(Distribution):
    """
    Layer-Controlled Galton Board distribution generator.
    Each layer has its own RX rotation angle or probability.
    """

    def __init__(self, device, angles=None, probs=None, optimizer="least_squares", target=None, **kwargs):
        """
        Initialize a LayerControlled distribution.

        Parameters:
            device: Quantum device instance.
            angles (list): RX gate angles for each layer.
            probs (list): Peg probabilities per layer.
            optimizer (str): Optimization method for target matching.
            target (list): Desired final distribution.
        """
        super().__init__(device, name = "Layer_Controlled", **kwargs)

        provided = [p is not None for p in (angles, target, probs)].count(True)
        self.angles = None
        self.target = None
        self.probs = None

        if provided != 1:
            raise ValueError("You must provide exactly one of 'angles', 'target', or 'probs'.")

        if angles is not None:
            if not isinstance(angles, list):
                raise TypeError("'angles' must be a list.")
            self.angles = angles

        elif target is not None:
            if not isinstance(target, list):
                raise TypeError("'target' must be a list.")
            self.optimizer = optimizer
            self.target = target

        elif probs is not None:
            if not isinstance(probs, list):
                raise TypeError("'probs' must be a list.")
            self.probs = probs

    def circuit(self, n_layers):
        """
        Build the quantum circuit for the layer-controlled Galton board.

        Parameters:
            n_layers (int): Number of layers.

        Returns:
            tuple: (Circuit function/object, measured wires, kwargs dictionary)
        """
        n = n_layers
        self.number_of_layers = n
        num_qubits = 2 * (n + 1)
        control_qubit = 0
        ball_qubit = n + 1
        ball_measure_wires = [ball_qubit + i for i in range(-n, n + 1, 2)]

        if self.angles is not None and len(self.angles) != n:
            raise ValueError("Length of 'angles' must match the number of layers.")
        elif self.probs is not None and len(self.probs) != n:
            raise ValueError("Length of 'probs' must match the number of layers.")
        elif self.target is not None and len(self.target) != n_layers + 1:
            raise ValueError("Length of 'target' must equal the number of final bins (n_layers + 1).")

        

        # Convert inputs to angles/probabilities
        if self.angles is not None:
            angles = self.angles
            self.probs = probabilities_from_rx_angles(angles)

        elif self.probs is not None:
            angles = rx_angles_from_probabilities(self.probs).tolist()

        elif self.target is not None:
            if self.optimizer == "least_squares":
                res = solve_galton_layer(target=self.target)
                if res.success:
                    probs = res.x
                else:
                    raise RuntimeError(f"Solver failed: {res.message}")
            angles = rx_angles_from_probabilities(probs).tolist()
        kwargs_dict = {"probs": self.probs}
        # Circuit for PennyLane default.qubit
        if self.device_name == "Pennylane_default.qubit":

            def peg(i):
                qml.CSWAP(wires=[control_qubit, i, i - 1])
                qml.CNOT(wires=[i, control_qubit])
                qml.CSWAP(wires=[control_qubit, i, i + 1])

            @qml.qnode(self.dev(wires=num_qubits))
            def LayerControlledCircuit():
                cnt = 0
                qml.RX(angles[cnt], wires=control_qubit)
                cnt += 1
                qml.PauliX(wires=ball_qubit)

                for layer in range(n):
                    positions = [
                        ball_qubit + pos
                        for pos in range(-layer, layer + 1, 2)
                        if 0 < ball_qubit + pos < num_qubits - 1
                    ]
                    for j, i in enumerate(positions):
                        peg(i)
                        if j < len(positions) - 1:
                            qml.CNOT(wires=[i + 1, control_qubit])

                    if layer < n - 1:
                        m = qml.measure(wires=control_qubit)
                        qml.cond(m, qml.PauliX)(wires=control_qubit)
                        qml.RX(angles[cnt], wires=control_qubit)
                        cnt += 1

                return qml.sample(wires=ball_measure_wires)

            return LayerControlledCircuit, ball_measure_wires, kwargs_dict

        # Circuit for Qiskit simulators and real devices
        elif self.device_name in ["Qiskit_AerSimulator", "Qiskit_FakeTorino", "IBM_Torino"]:

            def peg_qiskit(circ, i):
                circ.cswap(control_qubit, i, i - 1)
                circ.cx(i, control_qubit)
                circ.cswap(control_qubit, i, i + 1)

            def LayerControlledCircuitQiskit():
                circ = QuantumCircuit(num_qubits, len(ball_measure_wires))
                cnt = 0
                circ.rx(angles[cnt], control_qubit)
                cnt += 1
                circ.x(ball_qubit)

                for layer in range(n):
                    positions = [
                        ball_qubit + pos
                        for pos in range(-layer, layer + 1, 2)
                        if 0 < ball_qubit + pos < num_qubits - 1
                    ]
                    for j, i in enumerate(positions):
                        peg_qiskit(circ, i)
                        if j < len(positions) - 1:
                            circ.cx(i + 1, control_qubit)

                    if layer < n - 1:
                        circ.rx(angles[cnt], control_qubit)
                        cnt += 1

                for idx, wire in enumerate(ball_measure_wires):
                    circ.measure(wire, idx)

                return circ

            return LayerControlledCircuitQiskit, ball_measure_wires, kwargs_dict

    def ideal_distribution(self, **kwargs):
        """
        Compute the ideal probability distribution for the given layer probabilities.

        Parameters:
            probs (list): Probabilities per layer.

        Returns:
            dict: Mapping of bin index to probability.
        """
        p = kwargs["probs"]
        probs = galton_bin_probs_layer(p)
        dict_probs = {i: float(prob) for i, prob in enumerate(probs)}
        self.ideal_dist = dict_probs
        return dict_probs
