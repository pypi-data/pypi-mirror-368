import os
from typing import Optional

from generated.python import GeneratedPlanqkQuantumClient

from planqk.quantum.credentials import DefaultCredentialsProvider

_PLANQK_QUANTUM_API_BASE_URL_NAME = "PLANQK_QUANTUM_API_BASE_URL"


class PlanqkQuantumClient:
    def __init__(self, access_token: Optional[str] = None, organization_id: Optional[str] = None):
        base_url = os.environ.get(_PLANQK_QUANTUM_API_BASE_URL_NAME, "https://platform.planqk.de/quantum")
        credentials_provider = DefaultCredentialsProvider(access_token)

        self._client = GeneratedPlanqkQuantumClient(base_url=base_url, api_key=credentials_provider.get_access_token(),
                                                    organizationid=organization_id)
        self.backends = self._client.backends
        self.jobs = self._client.jobs
