# PLANQK Quatum Client

A Python SDK for accessing quantum computing backends through the PLANQK platform.

## Requirements

- Python 3.8 or higher
- Valid PLANQK access token
- Network access to PLANQK Quantum API endpoints

## Installation

The package is published on PyPI and can be installed via `pip`:

```bash
pip install --upgrade planqk-quantum-client
```

## Quick Start

### Basic Setup

```python
from planqk.quantum.client import PlanqkQuantumClient

# Initialize the client
client = PlanqkQuantumClient(
    access_token="your_access_token_here",
    organization_id="your_org_id"  # Optional
)
```

### Exploring Backends

```python
# List all available backends
backends = client.backends.get_backends()
for backend in backends:
    print(f"{backend['id']} - {backend['name']} ({backend['status']})")

# Get detailed backend information
backend_info = client.backends.get_backend("aws.ionq.aria")
print(f"Backend: {backend_info['name']}")

# Check backend status and availability
status = client.backends.get_backend_status("azure.ionq.simulator")
print(f"Status: {status['status']}")
```

### Submitting a Quantum Job

This example demonstrates how to submit a quantum circuit using the IonQ gate format.
The circuit applies a Hadamard gate to the first qubit (creating a superposition) and an X gate to the second qubit (flipping it to |1⟩), resulting in the state |+1⟩.

```python
ionq_input = AzureIonqJobInput(
    gateset="qis",
    qubits=2,
    circuits=[
        {"type": "h", "targets": [0]},
        {"type": "x", "targets": [1], "controls": [0]},
    ]
)

# Submit job to a simulator
job = self.client.jobs.create_job(
    backend_id=self.backend_id_azure,
    name="My Job",
    shots=1000,
    input=ionq_input,
    input_params={},
    input_format="IONQ_CIRCUIT_V1"
)

print(f"Job submitted with ID: {job['id']}")
print(f"Initial status: {job['status']}")

# Wait for completion and get results
job_id = job['id']
final_job = client.jobs.get_job(job_id)

if final_job['status'] == 'COMPLETED':
    results = final_job['results']
    print(f"Measurement counts: {results['measurement_counts']}")
    print(f"Execution time: {results['execution_duration']} seconds")
    # Expected output: {"01": ~500, "11": ~500} due to H gate on qubit 0 and X gate on qubit 1
elif final_job['status'] == 'FAILED':
    print(f"Job failed: {final_job.get('error_message', 'Unknown error')}")
```

## Documentation

For detailed API documentation, visit <https://docs.planqk.de/sdk-reference.html>.
