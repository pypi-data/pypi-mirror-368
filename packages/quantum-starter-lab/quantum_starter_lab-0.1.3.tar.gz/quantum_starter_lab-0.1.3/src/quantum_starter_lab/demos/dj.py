# src/quantum_starter_lab/demos/dj.py
# The user-facing function for the Deutsch-Jozsa demo.

from typing import Optional

from ..explain import get_dj_explanation
from ..ir.circuit import CircuitIR, Gate
from ..noise.spec import NoiseSpec
from ..results import Results
from ..runners import run


def deutsch_jozsa(
    n_qubits: int,
    oracle_type: str = "balanced",
    shots: int = 1024,
    noise_name: str = "none",
    p: float = 0.0,
    backend: str = "qiskit.aer",
    seed: Optional[int] = None,
) -> "Results":
    """
    Creates and runs the Deutsch-Jozsa algorithm.
    """
    # --- Build the Oracle ---
    oracle_ops = []
    if oracle_type == "constant":
        # For constant-0: do nothing
        oracle_ops = []
    elif oracle_type == "balanced":
        # Balanced: CNOT from alternating inputs
        oracle_ops = [
            Gate(name="cnot", qubits=[i, n_qubits])
            for i in range(n_qubits)
            if i % 2 == 0
        ]
    target_prep = [Gate(name="x", qubits=[n_qubits]), Gate(name="h", qubits=[n_qubits])]
    oracle_ops = target_prep + oracle_ops

    # --- Build the Full Circuit ---
    ir = CircuitIR(
        n_qubits=n_qubits + 1,  # One extra qubit for the oracle
        operations=[
            Gate(name="h", qubits=list(range(n_qubits))),
            Gate(name="x", qubits=[n_qubits]),
            Gate(name="h", qubits=[n_qubits]),
            *oracle_ops,
            Gate(name="h", qubits=list(range(n_qubits))),
        ],
    )

    noise_spec = NoiseSpec(name=noise_name, p=p)
    results = run(ir=ir, shots=shots, noise_spec=noise_spec, backend=backend, seed=seed)

    explanation = (
        f"The oracle was '{oracle_type}'. Measuring all zeros suggests a constant "
        f"function, while anything else suggests balanced. "
        f"{get_dj_explanation(n_qubits)}"
    )
    results.explanation = explanation

    return results
