from ....base.device import Device
from qiskit import QuantumCircuit, transpile, qasm2, qasm3
from qiskit_aer import AerSimulator
from collections import Counter


class QiskitAerSimulator(Device):
    """
    Noiseless Qiskit Aer simulator device.
    """

    def __init__(self, shots=1000):
        super().__init__("Qiskit_AerSimulator", shots)

    def __call__(self, wires):
        """Qiskit Aer does not require explicit device instantiation here."""
        return None

    def run_circuit(self, measure_wires, **kwargs):
        """
        Execute the circuit on the Qiskit AerSimulator and return one-hot probabilities.
        
        Args:
            measure_wires (list[int]): Wires to measure.
        """
        qc = self.circuit()
        simulator = AerSimulator()
        compiled = transpile(qc, simulator)
        job = simulator.run(compiled, shots=self.shots)
        result = job.result()
        raw_counts = result.get_counts()

        # Convert bitstrings to tuples
        samples = []
        for bitstring, count in raw_counts.items():
            bitstring = bitstring.replace(" ", "")
            bits = tuple(int(b) for b in reversed(bitstring))
            samples.extend([bits] * count)

        counts = Counter(samples)
        one_hot_probs = {}
        num_shots = self.shots
        n_wires = len(measure_wires)

        for bitstring in range(2 ** n_wires):
            bits = tuple(int(x) for x in format(bitstring, f'0{n_wires}b'))
            if sum(bits) == 1:
                prob = counts.get(bits, 0) / num_shots
                one_hot_probs[bits] = prob

        # Normalize probabilities
        total = sum(one_hot_probs.values())
        if total > 0:
            one_hot_probs = {k: v / total for k, v in one_hot_probs.items()}

        return one_hot_probs

    def draw_circuit(self, fold=-1):
        """Draw the Qiskit circuit as a Matplotlib figure."""
        fig = self.circuit().draw("mpl", fold=fold)
        return fig

    def export_qasm(self, version, filename="exported_circuit.txt"):
        """
        Export the circuit in OpenQASM format.
        
        Args:
            version (str): '2' or '3'.
            filename (str): Output file path.
        """
        if version == "2":
            qasm_str = qasm2.dumps(self.circuit())
        elif version == "3":
            qasm_str = qasm3.dumps(self.circuit())
        else:
            raise Exception("Version of OpenQASM must be '2' or '3'")

        with open(filename, "w") as f:
            f.write(qasm_str)
