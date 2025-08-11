from ...base.device import Device
from qiskit import transpile
from qiskit_ibm_runtime import SamplerV2, QiskitRuntimeService
from qiskit_ibm_runtime.fake_provider import FakeTorino
from qiskit.transpiler import generate_preset_pass_manager

from collections import Counter


class IBM_Torino(Device):
    """
    Interface for running quantum circuits on the IBM Torino backend 
    via Qiskit Runtime. Supports AI-based transpilation and post-processing 
    of results into one-hot probabilities.
    """

    def __init__(self, token: str, instance_CRN: str,optimization_level = 1, shots: int = 1000):
        """
        Initialize the IBM Torino device handler.

        Args:
            token (str): IBM Quantum API token.
            instance_CRN (str): IBM Quantum instance CRN string.
            optimization_level (int): Level of optimization for pass manager.
            shots (int, optional): Number of shots per execution. Defaults to 1000.

        """
        super().__init__("IBM_Torino", shots)
        self.token = token
        self.instance_CRN = instance_CRN
        self.opt_lvl = optimization_level

    def __call__(self, wires: int):
        """Reserved for future direct device instantiation if needed."""
        pass

    def run_circuit(self, **kwargs) -> str:
        """
        Run the stored quantum circuit on the IBM Torino backend.

        Returns:
            str: Job ID for the submitted run.
        """
        # Authenticate and get backend
        QiskitRuntimeService.save_account(
            token=self.token,
            instance=self.instance_CRN,
            overwrite=True
        )
        service = QiskitRuntimeService()
        backend = service.backend("ibm_torino")

        qc = self.circuit()

        sampler = SamplerV2(mode=backend)

        pm = generate_preset_pass_manager(backend=backend, optimization_level=self.opt_lvl)
        isa_circuit = pm.run(qc)

        
        job = sampler.run([isa_circuit], shots=self.shots)
        return job.job_id()

    def job_results(self, measure_wires: list[int], job_ID: str, **kwargs) -> dict:
        """
        Retrieve results for a completed IBM Torino job and compute
        normalized one-hot probabilities.

        Args:
            measure_wires (list[int]): List of wires to measure.
            job_ID (str): Job ID to retrieve results for.

        Returns:
            dict: Mapping of bitstring tuples to normalized probabilities.
        """
        QiskitRuntimeService.save_account(
            token=self.token,
            instance=self.instance_CRN,
            overwrite=True
        )
        service = QiskitRuntimeService()
        job = service.job(job_ID)
        result = job.result()

        counts = Counter()

        # Access measurement data
        c_obj = getattr(result[0].data, "c", None) or result[0].data.get("c", None)
        if c_obj is None:
            raise RuntimeError("No 'c' (shot memory) found in SamplerV2 result.")

        for bs in c_obj.get_bitstrings():
            bits = tuple(int(b) for b in reversed(bs))
            counts[bits] += 1

        # Compute one-hot probabilities (Hamming weight == 1)
        one_hot_probs = {}
        n_wires = len(measure_wires)
        for bit_val in range(2 ** n_wires):
            bits = tuple(int(x) for x in format(bit_val, f'0{n_wires}b'))
            if sum(bits) == 1:
                one_hot_probs[bits] = counts.get(bits, 0) / self.shots

        # Normalize probabilities
        total = sum(one_hot_probs.values())
        if total > 0:
            one_hot_probs = {k: v / total for k, v in one_hot_probs.items()}

        return one_hot_probs
