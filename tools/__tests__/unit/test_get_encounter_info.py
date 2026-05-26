import json

from unittest.mock import patch, MagicMock
from tools.get_encounter_info import get_encounter_info


@patch("tools.get_encounter_info.FhirProvider")
def test_get_encounter_info(mocked_fhir_provider: MagicMock):
    with open("tools/__tests__/mock_result.json") as file:
        mocked_result = json.load(file)

    instance = mocked_fhir_provider.return_value
    instance.bundle.return_value = mocked_result

    response = get_encounter_info("92689c00-79e4-43d7-9e7d-37b256bc4a8a")

    assert response == {"primary_info": mocked_result, "secondary_info": mocked_result}
