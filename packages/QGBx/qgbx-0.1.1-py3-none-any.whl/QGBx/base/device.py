from abc import ABC, abstractmethod
import pennylane as qml

class Device(ABC):
    """
    Abstract base class for quantum devices used in the Galton Board package.
    """

    def __init__(self, device_name, shots):
        """
        Initialize a quantum device.

        Args:
            device_name (str): Name of the quantum device.
            shots (int): Number of measurement shots.
        """
        self.device_name = device_name
        self.shots = shots
        self.circuit = None

    @abstractmethod
    def __call__(self, wires):
        """
        Initialize the device with the specified number of wires.

        Args:
            wires (int): Number of qubits/wires.
        """
        pass

    @abstractmethod
    def run_circuit(self, measure_wires, **kwargs):
        """
        Execute the stored quantum circuit.

        Args:
            measure_wires (list or None): Wires to measure.
            **kwargs: Additional device-specific arguments.
        """
        pass
