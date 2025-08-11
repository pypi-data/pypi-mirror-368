from ...base.distribution import Distribution
import pennylane as qml
import numpy as np
from ...utils import *
from qiskit import QuantumCircuit


class ExponentialOp(Distribution):
    """
    Optimized exponential distribution for Galton board simulation.
    Supports Pennylane and Qiskit-based devices.
    """

    def __init__(self, device, rate=1, reversed=False, RBS=1, **kwargs):
        super().__init__(device, "Exponential", **kwargs)
        self.rate = rate
        self.reversed = reversed
        self.RBS = RBS

    def circuit(self, n_layers):
        """
        Generate the exponential Galton board circuit.
        """
        n = n_layers
        self.number_of_layers = n
        num_qubits = n_layers + 1
        ball_qubit = n - 1
        ancilary = n + 1
        ball_measure_wires = [ball_qubit + i for i in range(-n, n + 1, 2)]

        target_exponential = list(
            self.ideal_distribution(
                interval_size=n + 1,
                rate=self.rate,
                reverse=self.reversed
            ).values()
        )

        res = solve_per_peg(N=n, target=target_exponential)
        if res.success:
            x = res.x
            offsets = flatten_indices(n + 1)
            flat_probs = []
            for i in range(n + 1):
                row_p = x[offsets[i]: offsets[i] + (i + 1)]
                row_p_reversed = row_p[::-1]
                flat_probs.extend(row_p_reversed)
            probs = flat_probs
        else:
            raise RuntimeError(f"Solver failed: {res.message}")

        angle_up = rx_angles_from_probabilities(1 - probs[0]).item()
        angles_down = rx_angles_from_probabilities(np.array(probs)).tolist()

        kwargs_dict = {
            "interval_size": n + 1,
            "rate": self.rate,
            "reverse": self.reversed
        }

        if self.device_name == "Pennylane_default.qubit":
            # Pennylane version can be implemented if needed
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
                    raise ValueError("Unknown Reconfigured Beamsplitter Type")

            def add_beamsplitteri(qc: QuantumCircuit, ctrl: int, tgt: int, theta: float, anc: int):
                if self.RBS == 1:
                    qc.cx(ctrl, anc)
                    qc.cry(theta, anc, ctrl)
                    qc.cx(ctrl, anc)
                    qc.cx(anc, tgt)
                    qc.reset(anc)
                elif self.RBS == 2:
                    qc.h(ctrl)
                    qc.cx(ctrl, anc)
                    qc.ry(theta / 2, ctrl)
                    qc.ry(theta / 2, anc)
                    qc.cx(ctrl, anc)
                    qc.h(ctrl)
                    qc.cx(anc, tgt)
                    qc.reset(anc)
                else:
                    raise ValueError("Unknown Reconfigured Beamsplitter Type")

            def gaussian_circuit():
                qc = QuantumCircuit(n + 2, n + 1)
                qc.x(ball_qubit)  # drop the ball
                count = 1

                for layer in range(n_layers):
                    for i in range(layer + 1):
                        if layer == 0:
                            add_beamsplitter(qc, ball_qubit + 1, ball_qubit, angle_up)
                        else:
                            if i == 0:
                                add_beamsplitter(
                                    qc,
                                    ball_qubit - layer,
                                    ball_qubit - layer + 1,
                                    angles_down[count]
                                )
                                count += 1
                            else:
                                ctrl = ball_qubit - layer + i
                                tgt = ctrl + 1
                                add_beamsplitteri(
                                    qc,
                                    tgt,
                                    ctrl,
                                    angles_down[count],
                                    ancilary
                                )
                                count += 1
                    qc.barrier()

                qc.measure(range(num_qubits), range(num_qubits))
                return qc

            return gaussian_circuit, ball_measure_wires, kwargs_dict

    def ideal_distribution(self, **kwargs):
        """
        Compute the ideal exponential probability distribution.
        """
        n = kwargs["interval_size"]
        rate = kwargs.get("rate", 1.0)
        reverse = kwargs.get("reverse", False)

        x = np.arange(n)
        probs = rate * np.exp(-rate * x)

        if reverse:
            probs = probs[::-1]

        probs /= np.sum(probs)
        dict_probs = {i: float(prob) for i, prob in enumerate(probs)}
        self.ideal_dist = dict_probs
        return dict_probs
