import pytest
from qiskit import QuantumCircuit
from aer_plugin.backends import AER


class TestRunCircuit:
    """
    Verify whether createing a circuit from different qasm versions return the correct outputs.
    """

    def test_invalid_qasm_version(self):
        """
        passing a qasm without specified version should raise a value error
        """

        with pytest.raises(ValueError):
            AER("", {}, "").circuit_from_qasm("./tests/invalid.qasm")

    def test_qasm3(self):
        """
        passing a qasm v3 file should return a valid quantum cirucit
        """

        circuit = AER("", {}, "").circuit_from_qasm("./tests/v3.qasm")

        assert isinstance(circuit, QuantumCircuit) is True

    def test_qasm2(self):
        """
        passing a qasm v2 file should return a valid quantum cirucit
        """

        circuit = AER("", {}, "").circuit_from_qasm("./tests/v2.qasm")

        assert isinstance(circuit, QuantumCircuit) is True
