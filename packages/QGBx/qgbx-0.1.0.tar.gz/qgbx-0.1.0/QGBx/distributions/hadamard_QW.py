from ..base.distribution import Distribution
from ..base.device import Device
import pennylane as qml
import numpy as np
from qiskit import QuantumCircuit


class HadamardQW(Distribution):
    """
    Hadamard Quantum Walk distribution generator for the Quantum Galton Board.
    Supports symmetric and asymmetric initial coin states.
    """

    def __init__(self, device, type="Symmetric", **kwargs):
        """
        Initialize the Hadamard quantum walk.

        Args:
            device: Quantum device instance.
            type (str): Type of quantum walk:
                - "Symmetric"
                - "Asymmetric_Right"
                - "Asymmetric_Left"
        """
        super().__init__(device, name = "Hadamard_QW", **kwargs)
        if type not in ["Symmetric", "Asymmetric_Right", "Asymmetric_Left"]:
            raise ValueError("Unknown Type of Quantum Walk")
        self.type = type

    def circuit(self, n_layers):
        """
        Create the quantum circuit for the Hadamard Quantum Walk.

        Args:
            n_layers (int): Number of Galton board layers.

        Returns:
            tuple: (Circuit function/Qiskit circuit, measurement wires, kwargs_dict)
        """
        num_qubits = 2 * (n_layers + 1)
        control_qubit = 0
        ball_qubit = n_layers + 1

        ball_measure_wires = [ball_qubit + i for i in range(-n_layers, n_layers + 1, 2)]
        kwargs_dict = {"steps": len(ball_measure_wires), "type": self.type}

        # --- Pennylane implementation ---
        if self.device_name == "Pennylane_default.qubit":

            def peg(i):
                qml.CSWAP(wires=[control_qubit, i, i - 1])
                qml.CNOT(wires=[i, control_qubit])
                qml.CSWAP(wires=[control_qubit, i, i + 1])

            @qml.qnode(self.dev(wires=num_qubits))
            def hadamardQwCircuit():
                if self.type == "Asymmetric_Right":
                    qml.PauliX(wires=control_qubit)

                qml.Hadamard(wires=control_qubit)

                if self.type == "Symmetric":
                    qml.S(wires=control_qubit)

                qml.PauliX(wires=ball_qubit)

                for layer in range(n_layers):
                    positions = [
                        ball_qubit + pos
                        for pos in range(-layer, layer + 1, 2)
                        if 0 < ball_qubit + pos < num_qubits - 1
                    ]
                    for j, i in enumerate(positions):
                        peg(i)
                        if j < len(positions) - 1:
                            qml.CNOT(wires=[i + 1, control_qubit])

                    if layer < n_layers - 1:
                        qml.Hadamard(wires=control_qubit)

                return qml.sample(wires=ball_measure_wires)

            return hadamardQwCircuit, ball_measure_wires, kwargs_dict

        # --- Qiskit implementation ---
        elif self.device_name in ["Qiskit_AerSimulator", "Qiskit_FakeTorino", "IBM_Torino"]:

            def peg(qc, i, ctrl):
                qc.cswap(ctrl, i, i - 1)
                qc.cx(i, ctrl)
                qc.cswap(ctrl, i, i + 1)

            def hadamardQwCircuit():
                qc = QuantumCircuit(num_qubits, len(ball_measure_wires))

                if self.type == "Asymmetric_Right":
                    qc.x(control_qubit)

                qc.h(control_qubit)

                if self.type == "Symmetric":
                    qc.s(control_qubit)

                qc.x(ball_qubit)

                for layer in range(n_layers):
                    positions = [
                        ball_qubit + pos
                        for pos in range(-layer, layer + 1, 2)
                        if 0 < ball_qubit + pos < num_qubits - 1
                    ]
                    for j, i in enumerate(positions):
                        peg(qc, i, control_qubit)
                        if j < len(positions) - 1:
                            qc.cx(i + 1, control_qubit)

                    if layer < n_layers - 1:
                        qc.h(control_qubit)

                qc.barrier()
                for idx, wire in enumerate(ball_measure_wires):
                    qc.measure(wire, idx)

                return qc

            return hadamardQwCircuit, ball_measure_wires, kwargs_dict

    def ideal_distribution(self, **kwargs):
        """
        Simulate a discrete Hadamard quantum walk and return the probability distribution.

        Keyword Args:
            steps (int): Number of steps (default: 10).
            type (str): Type of initial coin state.
                - "Symmetric"        → (|0⟩ - i|1⟩)/√2
                - "Asymmetric_Right" → (|0⟩ - |1⟩)/√2
                - "Asymmetric_Left"  → (|0⟩ + |1⟩)/√2

        Returns:
            dict: Mapping position index → probability.
        """
        steps = kwargs.get("steps", 10)
        init_type = kwargs.get("type", "Symmetric")
        steps -= 1

        size = 2 * steps + 1
        state = np.zeros((2, size), dtype=complex)

        # Initial coin state
        if init_type == "Symmetric":
            state[0, steps] = 1 / np.sqrt(2)
            state[1, steps] = -1j / np.sqrt(2)
        elif init_type == "Asymmetric_Right":
            state[0, steps] = 1 / np.sqrt(2)
            state[1, steps] = -1 / np.sqrt(2)
        elif init_type == "Asymmetric_Left":
            state[0, steps] = 1 / np.sqrt(2)
            state[1, steps] = 1 / np.sqrt(2)
        else:
            raise ValueError("Invalid type. Choose from 'Symmetric', 'Asymmetric_Right', 'Asymmetric_Left'.")

        # Hadamard coin operator
        hadamard = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]])

        for _ in range(steps):
            state = np.tensordot(hadamard, state, axes=([1], [0]))
            new_state = np.zeros_like(state)
            new_state[0, 1:] = state[0, :-1]   # |0⟩ → shift right
            new_state[1, :-1] = state[1, 1:]   # |1⟩ → shift left
            state = new_state

        probs = np.sum(np.abs(state) ** 2, axis=0)
        probs /= np.sum(probs)

        dict_probs = {i: float(prob) for i, prob in enumerate(probs)}
        dict_probs = {i: v for i, v in enumerate({k: v for k, v in dict_probs.items() if v != 0.0}.values())}

        self.ideal_dist = dict_probs
        return dict_probs
