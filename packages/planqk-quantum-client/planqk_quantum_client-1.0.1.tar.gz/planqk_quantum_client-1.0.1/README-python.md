# PLANQK Quantum Client

The PLANQK Quantum Client is a Python SDK for accessing quantum computing backends through the PLANQK platform.
It provides a low-level interface for direct interaction with quantum hardware and simulators, offering fine-grained control over job submission, backend management, and result retrieval.

A more detailed documentation of the client can be found [here](https://docs.platform.planqk.de/sdk-quantum-client-reference.html).

## Installation

The package is published on PyPI and can be installed via `pip` (Python 3.11 or higher is required):

```bash
pip install --upgrade planqk-quantum-client
```

## Quick Start

### Basic Setup

To get started with the PLANQK Quantum Client, you'll need a valid access token from the PLANQK platform.
You can obtain this from the PLANQK dashboard.

```python
from planqk.quantum.client import PlanqkQuantumClient

# Initialize the client
client = PlanqkQuantumClient(
    access_token="your_access_token_here"
)
```

### Exploring Backends

```python
# List all available backends
backends = client.backends.get_backends()
for backend in backends:
    print(f"{backend.id} - {backend.name}")

# Get detailed backend information
backend_info = client.backends.get_backend("aws.ionq.aria")
print(f"Backend: {backend_info.name}")
print(f"Qubits: {backend_info.configuration.qubit_count}")
print(f"Technology: {backend_info.technology}")
...

# Check backend status and availability
status = client.backends.get_backend_status("azure.ionq.simulator")
print(f"Status: {status.status}")
```

### Submitting a Quantum Job

This example demonstrates how to submit a quantum circuit using the IonQ native gate format.
The circuit applies a Hadamard gate to the first qubit (creating a superposition) and an X gate to the second qubit (flipping it to |1⟩), resulting in the state |+1⟩.

```python
from planqk.quantum.sdk import AzureIonqJobInput

# Define a quantum circuit using IonQ format
ionq_input = AzureIonqJobInput(
    gateset="qis",
    qubits=2,
    circuits=[
        {"type": "h", "targets": [0]},
        {"type": "x", "targets": [1], "controls": [0]},
    ]
)

# Submit job to a simulator
job = client.jobs.create_job(
    backend_id="azure.ionq.simulator",
    name="My Quantum Job",
    shots=1000,
    input=ionq_input,
    input_params={},
    input_format="IONQ_CIRCUIT_V1"
)

print(f"Job submitted with ID: {job.id}")
print(f"Initial status: {job.status}")

# Wait for completion and get results
job_id = job.id
final_job = client.jobs.get_job(job_id)

if final_job.status == 'COMPLETED':
    results = final_job.results
    print(f"Measurement counts: {results.measurement_counts}")
    print(f"Execution time: {results.execution_duration} seconds")
    # Expected output: {"01": ~500, "11": ~500} due to H gate on qubit 0 and X gate on qubit 1
elif final_job.status == 'FAILED':
    print(f"Job failed: {final_job.error_message}")
```

Different backends require specific input formats (in the example `AzureIonqJobInput`).
Therefore, the SDK provides backend-specific classes (see [documentation](https://docs.platform.planqk.de/sdk-quantum-client-reference.html#backend-specific-input-classes) for details).

**Important**: The client does not perform transpilation.
Input must match the target backend's capabilities and connectivity, including gates, qubits, and other backend-specific requirements.
