# planqk-api-sdk

This repository contains the SDK to access quantum backends via the PLANQK Quantum API.
The clients are generated from a [OpenAPI](https://swagger.io/specification) description using [Fern](https://buildwithfern.com).
The generated clients are a baseline, and the idea is to adapt and extend them to our specific needs.

## Generate the SDK clients with Fern

> <https://buildwithfern.com/docs/getting-started>

```bash
npm install -g fern-api
fern upgrade
fern generate
```

## Python Setup

To create a new virtual environment and install the dependencies, run:

```bash
uv venv
source .venv/bin/activate

uv sync
```

Update dependencies and lock files:

```bash
uv sync -U
```

## How to update the Python client?

After generating the SDK clients with Fern, check if the changes are compatible with our wrapper.

## License

Apache-2.0 | Copyright 2025 Kipu Quantum GmbH
