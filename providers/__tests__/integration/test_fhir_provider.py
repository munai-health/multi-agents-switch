from providers.fhir_provider import FhirProvider
from adapters.http_adapter import HttpAdapter


def test_http_adapter():
    http_adapter = HttpAdapter()
    fhir_provider = FhirProvider(http_adapter)

    bundle = {
        "resourceType": "Bundle",
        "type": "batch",
        "entry": [
            {
                "request": {
                    "method": "GET",
                    "url": "/Patient?_count=1",
                }
            }
        ],
    }

    response = fhir_provider.bundle(bundle)

    assert len(response['entry']) == 1
