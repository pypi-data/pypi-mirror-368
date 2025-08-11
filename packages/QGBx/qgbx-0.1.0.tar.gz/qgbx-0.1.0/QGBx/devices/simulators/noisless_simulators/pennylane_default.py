from ....base.device import Device
import pennylane as qml
from collections import Counter


class PennylanDefaultQubit(Device):
    """
    Pennylane noiseless simulator using the 'default.qubit' backend.
    """

    def __init__(self, shots=1000):
        super().__init__("Pennylane_default.qubit", shots)

    def __call__(self, wires):
        """Create the Pennylane default.qubit device."""
        return qml.device("default.qubit", wires=wires, shots=self.shots)

    def run_circuit(self, measure_wires, **kwargs):
        """
        Execute the circuit and return one-hot probability distribution.
        
        Args:
            measure_wires (list[int]): Wires to measure.
        """
        results = self.circuit()
        counts = Counter(tuple(sample) for sample in results)

        one_hot_probs = {}
        num_shots = self.shots
        n_wires = len(measure_wires)

        for bitstring in range(2 ** n_wires):
            bits = tuple(int(x) for x in format(bitstring, f'0{n_wires}b'))
            if sum(bits) == 1:
                prob = counts.get(bits, 0) / num_shots
                one_hot_probs[bits] = prob

        return one_hot_probs

    def draw_circuit(self, **kwargs):
        """Draw the circuit as a Matplotlib figure."""
        fig, ax = qml.draw_mpl(self.circuit)()
        return fig
