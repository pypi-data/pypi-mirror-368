from ....base.device import Device
from qiskit import qasm2, qasm3
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit_ibm_runtime.fake_provider import FakeTorino
from qiskit_ibm_transpiler import generate_ai_pass_manager
from qiskit.transpiler import generate_preset_pass_manager
from collections import Counter


class QiskitFakeTorino(Device):
    """
    Device interface for IBM's 'FakeTorino' backend simulation.
    """

    def __init__(self,ai_optimized =False,  optimization_level = 0, ai_optimization_level=0,  shots=1000):
        super().__init__("Qiskit_FakeTorino", shots)
        self.ai_op = ai_optimized
        self.op_lvl = optimization_level
        self.ai_op_lvl = ai_optimization_level

    def __call__(self, wires):
        """This simulator does not require explicit instantiation logic."""
        return None

    def run_circuit(self, measure_wires, **kwargs):
        """
        Run the circuit on the fake provider of IBM Torino backend to simulate its noise effect to a certain extent
        , and return one-hot probabilities.

        Args:
            measure_wires (list[int]): Wires to measure.
        """
        

        
        qc = self.circuit()
        backend = FakeTorino()
        if self.ai_op:
            # AI transpilation for Torino topology
            ai_transpiler = generate_ai_pass_manager(
                coupling_map = backend.coupling_map,
                ai_optimization_level = self.ai_op_lvl,
                optimization_level = self.op_lvl,
                ai_layout_mode = "optimize",
            )
            isa_circuit = ai_transpiler.run(qc)

        else:
            pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
            isa_circuit = pm.run(qc)

        # Simulate execution on FakeTorino
        
        sampler = SamplerV2(mode=backend)
        job = sampler.run([isa_circuit], shots=self.shots)
        result = job.result()

        # Extract counts from result
        counts = Counter()
        pub = result[0]
        c_obj = None
        if hasattr(pub.data, "get"):
            c_obj = pub.data.get("c", None)
        if c_obj is None and hasattr(pub.data, "c"):
            c_obj = pub.data.c
        if c_obj is None:
            raise RuntimeError("No 'c' (shot memory) found in SamplerV2 result.")

        for bitstring in c_obj.get_bitstrings():
            bits = tuple(int(b) for b in reversed(bitstring))
            counts[bits] += 1

        # Compute one-hot probabilities (Hamming weight == 1)
        one_hot_probs = {}
        n_wires = len(measure_wires)
        for bit_val in range(2 ** n_wires):
            bits = tuple(int(x) for x in format(bit_val, f"0{n_wires}b"))
            if sum(bits) == 1:
                one_hot_probs[bits] = counts.get(bits, 0) / self.shots

        # Normalize
        total = sum(one_hot_probs.values())
        if total > 0:
            one_hot_probs = {k: v / total for k, v in one_hot_probs.items()}

        return one_hot_probs

    def draw_circuit(self, fold=-1):
        """Draw the circuit as a Matplotlib figure."""
        return self.circuit().draw("mpl", fold=fold)

    def export_qasm(self, version, filename="exported_circuit.txt"):
        """
        Export the current circuit to OpenQASM format.

        Args:
            version (str): '2' or '3'.
            filename (str): Output file path.
        """
        if version == "2":
            qasm_str = qasm2.dumps(self.circuit())
        elif version == "3":
            qasm_str = qasm3.dumps(self.circuit())
        else:
            raise ValueError("Version of OpenQASM must be '2' or '3'.")

        with open(filename, "w") as f:
            f.write(qasm_str)
