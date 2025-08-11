from abc import ABC, abstractmethod
from .device import Device
import numpy as np

class Distribution(ABC):
    """
    Abstract base class for quantum distributions.

    Subclasses must implement:
    - `circuit()`: Defines the quantum circuit for the distribution.
    - `ideal_distribution()`: Returns the theoretical probability distribution.
    """

    def __init__(self, device=None, name=None, **kwargs):
        if not isinstance(device, Device):
            raise Exception("Device not recognized.")

        self.device_name = device.device_name
        self.name = name
        self.dev = device
        self.probs = None
        self.ideal_dist = None

    @abstractmethod
    def circuit(self, **kwargs):
        """
        Defines the quantum circuit for the distribution.

        Returns:
            tuple: Circuit, measurement wires, and additional arguments.
        """
        pass

    @abstractmethod
    def ideal_distribution(self, **kwargs):
        """
        Returns the ideal (theoretical) probability distribution.

        Returns:
            np.ndarray: Theoretical distribution.
        """
        pass
