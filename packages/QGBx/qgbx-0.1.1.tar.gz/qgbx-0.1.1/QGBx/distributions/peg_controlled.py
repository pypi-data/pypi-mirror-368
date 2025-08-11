from ..base.distribution import Distribution
from ..base.device import Device
import pennylane as qml
import numpy as np
from ..utils import (
    probabilities_from_rx_angles,
    reconstruct_original_rows,
    rx_angles_from_probabilities,
    solve_per_peg,
    flatten_indices,
    galton_bin_probs_flat
)
from qiskit import QuantumCircuit


class PegControlled(Distribution):
    """
    Peg-Controlled Galton Board distribution generator.
    Supports initialization via angles, probabilities, or target distribution.
    """

    def __init__(self, device, angles=None, probs=None, optimizer="least_squares", target=None, **kwargs):
        """
        Initialize a PegControlled distribution.

        Parameters:
            device: Quantum device instance.
            angles (list): RX gate angles for each peg.
            probs (list): Probabilities per peg.
            optimizer (str): Optimization method for target matching.
            target (list): Desired final distribution.
        """
        super().__init__(device, name = "Peg_Controlled", **kwargs)

        provided = [p is not None for p in (angles, target, probs)].count(True)
        self.angles = None
        self.target = None
        self.probs = None
        self.probs_arg = None

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
        Build the quantum circuit for the peg-controlled Galton board.

        Parameters:
            n_layers (int): Number of layers in the Galton board.

        Returns:
            tuple: (Circuit function/object, measured wires, kwargs dictionary)
        """
        n = n_layers
        self.number_of_layers = n
        num_qubits = 2 * (n + 1)
        control_qubit = 0
        ball_qubit = n + 1
        ball_measure_wires = [ball_qubit + i for i in range(-n, n + 1, 2)]
        

        if self.angles is not None and len(self.angles) != (n**2 + n) / 2:
            raise ValueError("Length of 'angles' must match the number of layers.")
        elif self.probs is not None and len(self.probs) != (n**2 + n) / 2:
            raise ValueError("Length of 'probs' must match the number of layers.")
        elif self.target is not None and len(self.target) != n_layers + 1:
            raise ValueError("Length of 'target' must equal the number of final bins (n_layers + 1).")

        # Convert inputs to angles and probabilities
        if self.angles is not None:
            angles = self.angles
            self.probs_arg = probabilities_from_rx_angles(reconstruct_original_rows(angles, n_layers))
        elif self.probs is not None:
            angles = rx_angles_from_probabilities(self.probs).tolist()
        elif self.target is not None:
            probs_arg = []
            probs = None
            if self.optimizer == "least_squares":
                res = solve_per_peg(N=len(ball_measure_wires) - 1, target=self.target)
                if res.success:
                    x = res.x
                    offsets = flatten_indices(len(ball_measure_wires))
                    flat_probs = []
                    for i in range(len(ball_measure_wires)):
                        row_probs = x[offsets[i]:offsets[i] + (i + 1)]
                        row_probs_reversed = row_probs[::-1]
                        probs_arg.extend([float(val) for val in row_probs])
                        flat_probs.extend([float(val) for val in row_probs_reversed])
                    probs = flat_probs
                else:
                    raise RuntimeError(f"Solver failed: {res.message}")

            angles = rx_angles_from_probabilities(probs).tolist()
            self.probs_arg = probs_arg
        kwargs_dict = {"n_layers": n_layers, "probs": self.probs_arg}
        # Circuit for PennyLane default.qubit
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
            def PegControlledCircuit():
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
                        if layer == 0:
                            peg(i)
                        else:
                            peg_i(i, angles[cnt])
                            cnt += 1
                        if j < len(positions) - 1:
                            qml.CNOT(wires=[i + 1, control_qubit])

                return qml.sample(wires=ball_measure_wires)

            return PegControlledCircuit, ball_measure_wires, kwargs_dict

        # Circuit for Qiskit simulators and real devices
        elif self.device_name in ["Qiskit_AerSimulator", "Qiskit_FakeTorino", "IBM_Torino"]:

            def peg(qc, i, ctrl):
                qc.cswap(ctrl, i, i - 1)
                qc.cx(i, ctrl)
                qc.cswap(ctrl, i, i + 1)

            def peg_i(qc, i, ctrl, angle, creg_idx):
                qc.reset(ctrl)
                qc.rx(angle, ctrl)
                qc.cswap(ctrl, i, i - 1)
                qc.cx(i, ctrl)
                qc.cswap(ctrl, i, i + 1)

            def PegControlledCircuit():
                qc = QuantumCircuit(num_qubits, len(ball_measure_wires))
                cnt = 0
                qc.rx(angles[cnt], control_qubit)
                cnt += 1
                qc.x(ball_qubit)

                for layer in range(n):
                    positions = [
                        ball_qubit + pos
                        for pos in range(-layer, layer + 1, 2)
                        if 0 < ball_qubit + pos < num_qubits - 1
                    ]
                    for j, i in enumerate(positions):
                        if layer == 0:
                            peg(qc, i, control_qubit)
                        else:
                            peg_i(qc, i, control_qubit, angles[cnt], 0)
                            cnt += 1
                        if j < len(positions) - 1:
                            qc.cx(i + 1, control_qubit)

                for idx, wire in enumerate(ball_measure_wires):
                    qc.measure(wire, idx)

                return qc

            return PegControlledCircuit, ball_measure_wires, kwargs_dict

    def ideal_distribution(self, **kwargs):
        """
        Compute the ideal probability distribution for the given number of layers.

        Parameters:
            n_layers (int): Number of layers in the Galton board.
            probs (list): Peg probabilities.

        Returns:
            dict: Mapping of bin index to probability.
        """
        n = kwargs["n_layers"]
        probs_pegs = kwargs["probs"]
        probs = galton_bin_probs_flat(probs_pegs, n)
        dict_probs = {i: float(prob) for i, prob in enumerate(probs)}
        self.ideal_dist = dict_probs
        return dict_probs
