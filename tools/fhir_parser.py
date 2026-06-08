from datetime import datetime
from html.parser import HTMLParser


# =============================================================================
# HTML STRIPPER — remove tags HTML dos summaries das ClinicalImpressions
# =============================================================================

class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def get_text(self):
        return " ".join(p.strip() for p in self.text_parts if p.strip())


def _strip_html(html: str) -> str:
    s = _HTMLStripper()
    s.feed(html)
    return s.get_text()


# =============================================================================
# HELPERS
# =============================================================================

def _entries(bundle: dict) -> list:
    return bundle.get("entry", [])


def _resource(entry: dict) -> dict:
    return entry.get("resource", {})


def _inner_entries(primary: dict, index: int) -> list:
    """Acessa primary['entry'][index]['resource']['entry']"""
    try:
        return _entries(_resource(_entries(primary)[index]))
    except (IndexError, KeyError):
        return []


def _calc_days(start_iso: str, end_iso: str = None) -> int | None:
    """Calcula os dias de internação usando a data final (se houver) ou a data atual."""
    try:
        start = datetime.fromisoformat(start_iso.replace("Z", ""))
        end = datetime.fromisoformat(end_iso.replace("Z", "")) if end_iso else datetime.now()
        return (end - start).days
    except Exception:
        return None


# =============================================================================
# PARSERS POR RECURSO
# =============================================================================

def _parse_patient(primary: dict) -> dict:
    entries = _inner_entries(primary, 0)
    if not entries:
        return {}
    r = _resource(entries[0])
    birth = r.get("birthDate", "")
    age = None
    if birth:
        try:
            age = (datetime.now() - datetime.fromisoformat(birth)).days // 365
        except Exception:
            pass
    return {
        "sexo": r.get("gender"),
        "idade": age,
        "data_nascimento": birth,
    }


def _parse_condicoes(primary: dict) -> list[dict]:
    result = []
    for e in _inner_entries(primary, 1):
        r = _resource(e)
        coding = (r.get("code") or {}).get("coding") or [{}]
        result.append({
            "cid": coding[0].get("code"),
            "descricao": coding[0].get("display"),
            "inicio": r.get("onsetDateTime"),
        })
    return result


def _parse_encounter(primary: dict) -> dict:
    entries = _inner_entries(primary, 2)
    if not entries:
        return {}

    # 1. Localiza o recurso Encounter principal
    encounter_entry = next(
        (e for e in entries if _resource(e).get("resourceType") == "Encounter"), None
    )
    if not encounter_entry:
        return {}

    r = _resource(encounter_entry)
    period = r.get("period", {})
    start = period.get("start")
    end = period.get("end")  # Pode ser None se o paciente ainda estiver internado

    # 2. Constrói um mapa de ID -> Recurso para todas as Locations incluídas no Bundle
    location_pool = {}
    for e in entries:
        res = _resource(e)
        if res.get("resourceType") == "Location":
            loc_id = res.get("id")
            if loc_id:
                location_pool[loc_id] = res

    # Helper interno para extrair o nome ou buscar recursivamente no nó pai (partOf)
    def resolve_location_name_and_uti(loc_id: str) -> tuple[str | None, bool]:
        if not loc_id or loc_id not in location_pool:
            return None, False
        
        loc_res = location_pool[loc_id]
        name = loc_res.get("name")
        
        # Critério de checagem de UTI no recurso atual
        is_uti = False
        name_lower = (name or "").lower()
        if "uti" in name_lower or "icu" in name_lower:
            is_uti = True
            
        # Também checa nos tipos e características do local atual
        for t in loc_res.get("type", []):
            for coding in t.get("coding", []):
                if (coding.get("code") or "").lower() in ["icu", "uti"]:
                    is_uti = True

        # Se o recurso faz parte de outro local (ex: Leito dentro da Unidade UTI Geral 3)
        part_of_ref = loc_res.get("partOf", {}).get("reference", "")
        if part_of_ref and "Location/" in part_of_ref:
            parent_id = part_of_ref.split("/")[-1]
            # Busca recursivamente os dados do local pai
            parent_name, parent_is_uti = resolve_location_name_and_uti(parent_id)
            is_uti = is_uti or parent_is_uti
            # Se o leito tiver um nome simples (ex: '5454'), concatena com o da unidade pai para clareza
            if name and parent_name:
                name = f"{parent_name} - {name}"
            elif parent_name:
                name = parent_name

        return name, is_uti

    # 3. Monta o histórico de localizações traduzindo os IDs para nomes reais
    locations_raw = r.get("location", [])
    locations = []
    esteve_uti = False

    for loc in locations_raw:
        ref = loc.get("location", {}).get("reference") or ""
        loc_id = ref.split("/")[-1] if "Location/" in ref else None
        
        # Resolve dinamicamente o nome final e a validação de UTI
        nome_real, local_eh_uti = resolve_location_name_and_uti(loc_id)
        if local_eh_uti:
            esteve_uti = True

        locations.append({
            "nome": nome_real,
            "periodo_inicio": (loc.get("period") or {}).get("start"),
            "periodo_fim": (loc.get("period") or {}).get("end"),
            "status": loc.get("status"),
        })

    return {
        "tempo_internacao_dias": _calc_days(start, end) if start else None,
        "data_admissao": start,
        "data_alta": end,
        "status": r.get("status"),
        "esteve_uti": esteve_uti,
        "historico_localizacoes": locations,
    }

def _parse_procedimentos(primary: dict) -> list[dict]:
    result = []
    for e in _inner_entries(primary, 4):
        r = _resource(e)
        coding = ((r.get("code") or {}).get("coding") or [{}])
        result.append({
            "nome": coding[0].get("display") or (r.get("code") or {}).get("text"),
            "status": r.get("status"),
            "data": r.get("authoredOn"),
        })
    return result


def _parse_evolucoes(secondary: dict) -> list[dict]:
    result = []
    entries = _inner_entries(secondary, 0)
    for e in entries:
        r = _resource(e)
        summary_html = r.get("summary", "")
        result.append({
            "data": r.get("effectiveDateTime"),
            "tipo": ((r.get("code") or {}).get("coding") or [{}])[0].get("code"),
            "texto": _strip_html(summary_html) if summary_html else None,
        })
    # Ordena por data decrescente
    result.sort(key=lambda x: x["data"] or "", reverse=True)
    return result


def _parse_antibioticos(secondary: dict) -> list[dict]:
    result = []
    entries = _inner_entries(secondary, 1)
    for e in entries:
        r = _resource(e)
        coding = ((r.get("medicationCodeableConcept") or {}).get("coding") or [{}])
        dosage = (r.get("dosageInstruction") or [{}])[0]
        route = ((dosage.get("route") or {}).get("coding") or [{}])[0].get("display")
        dose_qty = (dosage.get("doseAndRate") or [{}])[0]
        dose = (dose_qty.get("doseQuantity") or {})
        result.append({
            "nome": coding[0].get("display") or (r.get("medicationCodeableConcept") or {}).get("text"),
            "status": r.get("status"),
            "data_inicio": r.get("authoredOn"),
            "via": route,
            "dose": f"{dose.get('value')} {dose.get('unit')}" if dose.get("value") else None,
        })
    return result


def _parse_historico_munai_score(secondary: dict) -> list[dict]:
    """
    Extrai o histórico do Munai Score localizando o valor decimal
    dentro dos recursos embutidos em 'contained'.
    """
    result = []
    
    secondary_entries = _entries(secondary)
    if len(secondary_entries) < 3:
        return []
        
    history_bundle = _resource(secondary_entries[2])
    
    if history_bundle.get("resourceType") == "Observation":
        records = [{"resource": history_bundle}]
    else:
        records = _entries(history_bundle)
        
    for e in records:
        r = _resource(e)
        if not r:
            continue
            
        score_value = None
        
        # 1. Procura primeiro dentro dos recursos embutidos ('contained')
        contained_resources = r.get("contained", [])
        for sub_res in contained_resources:
            # Varre os componentes do recurso contido
            for c in sub_res.get("component", []):
                if "valueQuantity" in c and "value" in c["valueQuantity"]:
                    score_value = c["valueQuantity"]["value"]
                    break # Encontrou o decimal (ex: 3.64), pode parar o loop interno
            if score_value is not None:
                break # Sai do loop do contained se já achou o valor
                
        # 2. Fallback de segurança: se não achou no contained, tenta nos componentes da raiz
        if score_value is None:
            for c in r.get("component", []):
                if "valueQuantity" in c and "value" in c["valueQuantity"]:
                    score_value = c["valueQuantity"]["value"]
                    break

        # 3. Se capturou o score decimal com sucesso, mapeia a data
        if score_value is not None:
            period = r.get("effectivePeriod") or {}
            data_registro = (
                r.get("effectiveDateTime") 
                or period.get("start") 
                or r.get("meta", {}).get("lastUpdated")
            )
            
            result.append({
                "data": data_registro,
                "score": {
                    "Munai Score": score_value
                }
            })
            
    # Ordena por data decrescente (mais recente primeiro)
    result.sort(key=lambda x: x["data"] or "", reverse=True)
    return result


# =============================================================================
# INTERFACE PÚBLICA
# =============================================================================

def parse_encounter_data(encounter_data: dict) -> dict:
    """
    Recebe o retorno de get_encounter_info() e extrai campos estruturados.

    Hemograma e PCR NÃO são extraídos aqui — estão no HTML das evoluções
    e serão extraídos pelo agente resumo via LLM.

    Returns:
        Dict estruturado pronto para o agente resumo.
    """
    primary = encounter_data.get("primary_info", {})
    secondary = encounter_data.get("secondary_info", {})

    return {
        "paciente":         _parse_patient(primary),
        "condicoes":        _parse_condicoes(primary),
        "encounter":        _parse_encounter(primary),
        "procedimentos":    _parse_procedimentos(primary),
        "evolucoes":        _parse_evolucoes(secondary),
        "historico_munai_score": _parse_historico_munai_score(secondary),
    }