import json
from langchain_core.messages import SystemMessage, HumanMessage
from config import llm_summarizer

SYSTEM_PROMPT = """You are a clinical data analyst for an antibiotic stewardship program. Your sole task is to extract, structure, and summarize patient data from FHIR records into a concise clinical report. 

You must maintain neutrality: do not make clinical decisions, do not judge if the patient is fit for a switch, and do not suggest alternative medications. Focus entirely on accurate data extraction.

INSTRUCTIONS:
- Extract laboratory results and vital signs embedded as plain text inside the 'evolucoes' field.
- Format all dates as DD/MM/YYYY.
- If any requested parameter is not found in the texts or structured data, write "Não localizado".

Output format (use exactly these section headers):

## Identificação e Curso Hospitalar
- **Paciente:** [Idade, sexo]
- **Admissão:** [Data de admissão]
- **Alta:** [Data de alta, se houver, ou "Paciente ainda internado"]
- **Tempo de Internação:** [X] dias
- **Diagnóstico:** [CID principal e descrição]

## Histórico de Localizações e UTI
- **Histórico:** [Liste a cronologia de unidades/leitos por onde o paciente passou com períodos]
- **Passagem por UTI:** [Sim/Não, detalhando qual unidade se aplicável]

## Sinais Vitais Relatados (Últimas 24-48h)
*Extraia ativamente das notas clínicas ('evolucoes')*
- **Temperatura:** [Registros de temperatura nas últimas 24-48h, destacando se houve febre >= 38°C]
- **Frequência Cardíaca (FC):** [Valores relatados em bpm]
- **Frequência Respiratória (FR):** [Valores relatados em irpm]
- **Pressão Arterial (PA):** [Valores relatados ou relatos de hipotensão/estabilidade]

## Exames Laboratoriais e Marcadores Inflamatórios
*Extraia o histórico e tendências das notas clínicas ('evolucoes')*
- **Hemograma:** [Contagem de Leucócitos/Glóbulos Brancos (WCC), Neutrófilos, Hemoglobina e Plaquetas com respectivas datas]
- **Marcadores de Inflamação:** [Valores de PCR e/ou Procalcitonina com respectivas datas]

## Condições do Trato Gastrointestinal e Via Oral
*Extraia relatos das notas clínicas sobre a capacidade de absorção e ingestão*
- **Status Nutricional/Via:** [Relatos sobre aceitação da via oral, dieta livre, jejum, ou uso de sondas (SNG/SNE)]
- **Sintomas GI:** [Presença ou ausência de relatos de vômitos, náuseas, diarreia, disfagia ou má absorção]

## Histórico do Munai Score (Probabilidade de Óbito)
- **Explicação**: Considere que o Munai Score é a probabilidade de obito do paciente.
- **Evolução Cronológica:** [Liste os scores extraídos do histórico do mais recente ao mais antigo no formato (DD/MM/YYYY: Valor). Indique a faixa do último score: 0-4 Baixo, 4-6 Médio, 6-8 Alto, >8 Altíssimo]

## Antibioticoterapia Registrada
- **Histórico de Antimicrobianos:** [Nome do medicamento, dose, via de administração, status e data de início de cada um presente nos dados estruturados]

## Procedimentos Realizados
- **Lista de Procedimentos:** [Apenas procedimentos cirúrgicos ou invasivos extraídos dos dados estruturados com suas respectivas datas]

## Síntese Evolutiva Recente
- [Breve resumo factual das últimas notas médicas/enfermagem focando na evolução geral do paciente, relatos de melhora/piora clínica e intercorrências registradas. Não faça recomendações]."""


def summarize_patient(parsed_data: dict) -> str:
    """
    Recebe o dict do fhir_parser e retorna um resumo clínico analítico,
    estruturando os dados conforme as necessidades do programa de stewardship.
    """
    # Enviamos as últimas 7 evoluções para garantir que o modelo consiga 
    # buscar os sinais vitais e exames da janela das últimas 48 horas.
    payload = {
        **parsed_data,
        "evolucoes": parsed_data.get("evolucoes", [])[:7],
        "historico_munai_score": parsed_data.get("historico_munai_score", [])[:5],
        "procedimentos": parsed_data.get("procedimentos", [])[:20],
    }

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(payload, ensure_ascii=False, default=str)),
    ]

    response = llm_summarizer.invoke(messages)
    return response.content