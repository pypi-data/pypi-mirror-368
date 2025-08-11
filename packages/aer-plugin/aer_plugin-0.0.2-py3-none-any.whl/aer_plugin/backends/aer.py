from qiskit import QuantumCircuit
from ..interface import ResultType, QasmFilePath, Metadata, Results
from .base_backend import BaseBackend


class AER(BaseBackend):
    """
    Default AER simulator handler class.
    """

    def __init__(
        self, qasm_file_path: QasmFilePath, metadata: Metadata, result_type: ResultType
    ):
        # pylint: disable=useless-parent-delegation
        super().__init__(qasm_file_path, metadata, result_type)

    def _exec_expval(self, circuit: QuantumCircuit) -> Results:
        """Extracts expval using EstimatorV2"""

        obs_list = self._metadata.get("obs")
        assert (
            obs_list is not None and len(obs_list) > 0 and isinstance(obs_list, list)
        ), "You need to provide the observables to get the expectation value!"

        # pylint: disable=import-outside-toplevel
        from qiskit_aer.primitives import EstimatorV2
        from qiskit.quantum_info import SparsePauliOp

        estimator = EstimatorV2()
        results = estimator.run(
            [(circuit, SparsePauliOp.from_list(obs)) for obs in obs_list]
        ).result()

        return [result.data.evs for result in results]  # type: ignore

    def _exec_counts(self, circuit: QuantumCircuit) -> Results:
        """Extracts counts using AerSimulator directly"""

        # pylint: disable=import-outside-toplevel
        from qiskit_aer import AerSimulator

        sim = AerSimulator()
        shots = self._get_shots()
        result = sim.run(circuit, shots=shots).result()

        return result.get_counts()  # type: ignore[no-any-return]

    def _get_shots(self) -> int:
        """Ensure that shots is always a number, even when user hasn't set anything."""

        shots = self._metadata.get("shots")
        if not shots:
            return 1000

        return int(shots)  # to ensure that shots will be a integer (for mypy)

    def _exec_quasi_dist(self, circuit: QuantumCircuit) -> Results:
        """Extracts quasi dist using SamplerV1"""

        # pylint: disable=import-outside-toplevel
        from qiskit_aer.primitives import Sampler

        sampler = Sampler()
        shots = self._get_shots()
        result = sampler.run([circuit], shots=shots).result()

        return dict(result.quasi_dists[0])  # type: ignore[no-any-return]

    def run_circuit(self) -> Results:
        """
        Execute the circuit aiming to get the required output type.

        It first creates the circuit from your qasm file, and the execute
        it using AER.
        """
        execution_types = {
            "expval": self._exec_expval,
            "counts": self._exec_counts,
            "quasi_dist": self._exec_quasi_dist,
        }

        circuit = self.circuit_from_qasm(self._qasm_file_path)

        execution_method = execution_types[self._result_type]
        return execution_method(circuit)
