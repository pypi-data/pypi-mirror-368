from abc import ABC
from typing import Optional
from qiskit import QuantumCircuit
from ..interface import ResultType, QasmFilePath, Metadata


QasmVersion = Optional[int]


class BaseBackend(ABC):
    """
    Base object for AER backends
    """

    def __init__(
        self, qasm_file_path: QasmFilePath, metadata: Metadata, result_type: ResultType
    ):
        self._result_type = result_type
        self._qasm_file_path = qasm_file_path
        self._metadata = metadata

    def _get_qasm_version(self, qasm_file_path: QasmFilePath) -> QasmVersion:
        """
        Search for OPENQASM header that specifies the qasm version
        """

        with open(qasm_file_path, "r", encoding="utf-8") as qasm_file:
            while True:
                line = qasm_file.readline().replace("\n", "").strip()

                if not line:
                    break

                is_v2 = line == "OPENQASM 2.0;"
                is_v3 = line == "OPENQASM 3.0;"

                if is_v2:
                    return 2
                if is_v3:
                    return 3

        return None

    def circuit_from_qasm(self, qasm_file_path: QasmFilePath) -> QuantumCircuit:
        """
        translate qasm code into a qiskit circuit
        """

        version = self._get_qasm_version(qasm_file_path)

        if version is None:
            raise ValueError("Your Qasm file has no version descriptor")

        if version == 2:
            return QuantumCircuit.from_qasm_file(qasm_file_path)  # type: ignore

        # pylint: disable=import-outside-toplevel
        from qiskit import qasm3

        return qasm3.load(qasm_file_path)  # type: ignore
