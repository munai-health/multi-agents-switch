from datetime import datetime, timedelta
from adapters.http_adapter import HttpAdapter
from providers.fhir_provider import FhirProvider
from typing import Any


def get_encounter_info(encounter_id: str) -> dict[str, Any]:
    fhir_provider = FhirProvider(HttpAdapter())

    primary_bundle = {
        "resourceType": "Bundle",
        "type": "batch",
        "entry": [
            {
                "request": {
                    "method": "GET",
                    "url": f"/Patient?_has:Encounter:patient:_id={encounter_id}",
                }
            },
            {
                "request": {
                    "method": "GET",
                    "url": f"/Condition?encounter={encounter_id}&clinical-status=active&code=http://hl7.org/fhir/sid/icd-10|",
                }
            },
            {
                "request": {
                    "method": "GET",
                    "url": f"/Encounter?_id={encounter_id}&_include=Encounter:location&_include:iterate=Location:partof",
                }
            },
            {
                "request": {
                    "method": "GET",
                    "url": f"/Observation?encounter={encounter_id}&code=https://munai.com.br/CodeSystem/protocol-type|MUNAI-SCORE",
                }
            },
            {
                "request": {
                    "method": "GET",
                    "url": f"/ServiceRequest?encounter={encounter_id}&category=https://fhirsync.munai.systems/NamingSystem/service-request-category|procedure&_count=50",
                }
            },
        ],
    }

    primary_info = fhir_provider.bundle(primary_bundle)

    encounter_end_date: str | None = primary_info['entry'][2]['resource']['entry'][0]['resource']['period'].get('start')
    munai_score_risk_assessment_id: str = primary_info['entry'][3]['resource']['entry'][0]['resource']['id']

    if encounter_end_date is None or munai_score_risk_assessment_id is None:
        return {
            "primary_info": primary_info
        }

    offset_date = (datetime.fromisoformat(encounter_end_date) - timedelta(days=3)).isoformat()

    secondary_bundle = {
        "resourceType": "Bundle",
        "type": "batch",
        "entry": [
            {
                "request": {
                    "method": "GET",
                    "url": f"/ClinicalImpression?encounter={encounter_id}&code=https://connector-ci.munai.systems/CodeSystem/clinical-impression-type|medical-evolution-report,nursing-evolution&date=ge{offset_date}",
                }
            },
            {
                "request": {
                    "method": "GET",
                    "url": f"/MedicationRequest?encounter={encounter_id}&code=https://connector-ci.munai.systems/NamingSystem/medication-class|495&date=ge{offset_date}",
                }
            },
            {
                "request": {
                    "method": "GET",
                    "url": f"/Observation/{munai_score_risk_assessment_id}/_history?_count=10",
                }
            },
        ],
    }

    secondary_info = fhir_provider.bundle(secondary_bundle)

    return {
        "primary_info": primary_info,
        "secondary_info": secondary_info,
    }
