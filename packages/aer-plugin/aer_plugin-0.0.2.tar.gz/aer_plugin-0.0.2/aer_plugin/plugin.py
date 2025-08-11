import os
from .interface import (
    PluginInterface,
    Backend,
    Metadata,
    ResultType,
    QasmFilePath,
    check_backend,
    check_result_type,
    check_qasm_file,
    Results,
)
from .backends import AER


class Plugin(PluginInterface):
    """
    The Plugin class is the starting point for quantum-plugins.
    Using this, the server worker can interect directly with
    simulators.
    """

    def __init__(self):
        current_file_path = os.path.dirname(__file__)
        backends_relative_path = os.path.join(current_file_path, "backends.txt")

        with open(backends_relative_path, "r", encoding="UTF-8") as file:
            backends = list(map(lambda x: x.replace("\n", ""), file))
            super().__init__(backends)

    @check_backend
    @check_result_type
    @check_qasm_file
    def execute(
        self,
        target_backend: Backend,
        qasm_file_path: QasmFilePath,
        metadata: Metadata,
        result_type: ResultType,
    ) -> Results:
        backends_handlers = {"aer": AER}

        backend_instance = backends_handlers[target_backend](
            qasm_file_path, metadata, result_type
        )

        return backend_instance.run_circuit()
