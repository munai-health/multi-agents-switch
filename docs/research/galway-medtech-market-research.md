# Oportunidades de produto no cluster de medtech de Galway

Pesquisa de mercado sobre o cluster de dispositivos médicos de Galway/Irlanda, dores identificadas e hipóteses estratégicas para posicionar a tecnologia de agentes de IA clínicos da Munai Health junto a essas empresas.

> Relatório completo e navegável (com tabelas, cards de hipóteses e fontes clicáveis):
> https://claude.ai/code/artifact/7493b752-2f73-4ac3-ac04-32b5c8672e4e

## 1. Panorama do mercado

Galway é, proporcionalmente, a maior concentração de fabricantes de dispositivos médicos do mundo:

- **100+** empresas de medtech na região de Galway
- **15.000** empregos diretos em medtech só em Galway
- **8 das 10** maiores medtechs do mundo têm base em Galway
- **€20 bi** em exportações do setor medtech irlandês por ano
- **50.000** empregos diretos em medtech na Irlanda (crescimento de ~3%/ano, projeção de 56.000 até 2028)
- **500+** empresas de medtech no país, 400+ de origem irlandesa
- **US$300 M**: investimento da Dexcom na primeira fábrica europeia, em Galway

Principais players: Medtronic, Boston Scientific, Abbott, Stryker, Johnson & Johnson MedTech (Cerenovus), Dexcom, Aerogen, Integer, TE/Creganna, Zimmer Biomet, Merit Medical (multinacionais); Neurent Medical, AuriGen Medical, ICS Medical Devices e Advant Medical (scale-ups locais, mais ágeis para pilotos).

Sinal mais relevante: a **Medtronic acabou de abrir em Galway um centro global de excelência em saúde digital cardíaca**, com 85 vagas para construir plataformas cloud que conectam paciente, clínico e dispositivo implantado em tempo real — evidência direta de que o cluster está migrando de "hardware puro" para "dispositivo + software + dados clínicos".

## 2. Sinais de 2025–2026

- **Software vira o produto**: o discurso do setor mudou de apps isolados para ecossistemas de software integrados (diagnóstico, monitoramento, apoio à decisão, automação de fluxo), com modelos de receita recorrente.
- **IA capturando o funding**: 55% de todo o venture funding em health tech em 2025 (vs. 37% em 2024) foi para empresas de IA.
- **Regulação sobrecarregando empresas pequenas**: MDR (evidência clínica + vigilância pós-mercado) e AI Act (dispositivos com IA) se sobrepõem, sem padrão único — a Comissão Europeia abriu revisão do MDR/IVDR em dez/2025.
- **Vigilância pós-mercado não escala manualmente**: mercado de plataformas de vigilância com IA crescendo ~23%/ano, mas ferramentas mal calibradas podem "enterrar" um evento reportável na fila enquanto o prazo do MDR corre.

**Por que isso importa para a Munai**: a arquitetura já construída no avaliador IV-to-oral (agentes especializados, revisor adversarial, trilha de auditoria CONSENSO/DECISOR/REVISOR/JULGAMENTO DO CURADOR) é o padrão de design que o mercado europeu de medtech está pedindo para compliance e vigilância — velocidade de IA com rastreabilidade auditável.

## 3. Onde está a dor

1. Relatórios de Avaliação Clínica (CER) sob o MDR — revisão sistemática de literatura contínua, cara e manual.
2. Compliance duplo MDR + AI Act — documentação técnica e avaliação de risco sem padrão único.
3. Triagem de eventos adversos / vigilância pós-mercado — volume de queixas maior que a capacidade humana.
4. Interoperabilidade de dados de dispositivo conectado com prontuário (FHIR/HL7) — dado de alta frequência não cabe bem em EHRs tradicionais.
5. Apoio à decisão clínica embarcado em software companheiro de dispositivo conectado — exatamente o que o hub da Medtronic em Galway está contratando para construir.
6. Evidência do mundo real (RWE) e dados federados via European Health Data Space (EHDS) — infraestrutura ainda imatura.
7. Entrada de empresas irlandesas em novos mercados (Brasil/LatAm) — barreira regulatória (ANVISA) e desconhecimento do sistema de saúde local.

## 4. Possibilidades de produto

| # | Oportunidade | Fit com a stack atual |
|---|---|---|
| 1 | Copiloto de Relatório de Avaliação Clínica (CER) | Reuso quase direto do padrão investigador (RAG/ReAct) + decisor + revisor + curador |
| 2 | Agente de triagem de vigilância pós-mercado | Reuso quase direto do mesmo pipeline aplicado a reclamações/eventos adversos |
| 3 | Documentação técnica para conformidade dupla MDR + AI Act | Adaptação — mapeamento de requisitos dos dois regimes |
| 4 | Camada de apoio à decisão clínica embarcável (FHIR-native) | Produto plataforma — parser FHIR determinístico + orquestração de agentes como SDK |
| 5 | Assistente de evidência federada (EHDS/RWE) | Aposta de médio prazo, monitorar |
| 6 | Ponte de entrada Brasil ↔ Irlanda | Go-to-market via Enterprise Ireland (escritório Brasil), não é produto em si |

## 5. Hipóteses a validar, em ordem de prioridade

**H1** — Scale-ups de Galway (50–500 funcionários) com produto com componente de software/IA pagariam por um copiloto auditável de CER.
*Validar com: 8–10 entrevistas com Regulatory/Clinical Affairs, via rede de ex-fellows da BioInnovate e Irish Medtech Association.*

**H2** — Times de vigilância pós-mercado temem "blind spots" que estourem prazos do MDR por triagem manual insuficiente.
*Validar com: entrevistas com Quality/RA leads; casos públicos de não-conformidade MDR.*

**H3** — Quem constrói software companheiro para dispositivos conectados prefere licenciar uma camada de decisão clínica explicável a construir do zero.
*Validar com: outreach a Aerogen, Neurent, AuriGen e ao hub da Medtronic PCS.*

**H4** — Empresas irlandesas de medtech querem um parceiro local para entrar no Brasil/LatAm, e a Munai (sede no Brasil, domínio de compliance clínico local) pode ser esse parceiro.
*Validar com: contato com Enterprise Ireland (Market Access, escritório Brasil) e desk de exportação da Irish Medtech Association.*

**H5** — Demanda por agentes de consulta a evidência federada (EHDS) ainda é prematura; revisitar em 2027.

## 6. Plano de ação recomendado

Priorizar **H1 e H2**: reaproveitam mais diretamente a arquitetura já construída, atacam uma dor com orçamento obrigatório (compliance não é opcional) e têm interlocutor claro.

1. Descoberta (4–6 semanas): 10–15 entrevistas com Regulatory/Clinical/Quality Affairs em Galway.
2. Teste de proposta de valor: landing page/one-pager em inglês com 2–3 propostas distintas.
3. MVP com design partners: focar em 1 caso de uso com scale-ups locais (mais ágeis que multinacionais).
4. Explorar parceria com BioInnovate Ireland (afiliada europeia da Stanford Biodesign) e o escritório da Enterprise Ireland no Brasil.
5. Aproveitar a janela da revisão do MDR/IVDR (anunciada em dez/2025) — empresas mais abertas a repensar ferramenta nesse momento.

## 7. Riscos e contrapontos

- Ciclo de venda B2B regulado é longo (6–18 meses) — priorizar scale-ups locais sobre multinacionais para tração inicial.
- Se o output entrar no dossiê regulatório oficial, pode ser exigido QMS próprio (ISO 13485) da Munai como fornecedora — um "copiloto interno de rascunho" tem barreira de entrada menor que um componente formal do SaMD.
- IA "adaptativa"/self-learning é vista com desconfiança por notified bodies sem validação rígida — posicionar como human-in-the-loop com trilha de auditoria é a vantagem competitiva natural da arquitetura atual.
- Distância física, fuso e idioma podem pesar contra abordagem 100% remota nesse mercado.
- Concorrência já existe (grandes players e startups de nicho em IA regulatória) — diferenciação deve vir da arquitetura auditável multiagente e do histórico em ambiente hospitalar altamente regulado (ANVISA).

## Fontes

- [Irish medtech companies to watch in 2026 — ThinkBusiness](https://www.thinkbusiness.ie/articles/irish-medtech-life-sciences-healthtech-companies-to-watch-2026/)
- [Medtronic estabelece hub de software europeu em Galway — Business & Finance](https://businessandfinance.com/news/fdi-of-the-month-may-2026-medtronic-establishes-european-software-hub-in-galway/)
- [Galway MedTech Hub — University of Galway](https://www.bioinnovate.ie/bioinnovate/about-us/galwaymedtechhub/)
- [Medtech Ireland: Galway, €20bn em exportações e 50.000 empregos](https://enable-research.ie/medtech-ireland/)
- [Lista completa de empresas de dispositivos médicos em Galway — Pharmchoices](https://pharmchoices.com/list-of-medical-device-companies-in-galway-2/)
- [Setor medtech irlandês atinge €20bi em exportações — IBEC](https://www.ibec.ie/connect-and-learn/media/2025/09/09/medtech-awards-25)
- [MedTech Sector: Shaping the Future — IDA Ireland](https://www.idaireland.com/explore-your-sector/business-sectors/medtech)
- [Medtronic Expands Galway Digital Health Hub — IDA Ireland](https://www.idaireland.com/latest-news/press-release/medtronic-announces-european-software-development-hub-in-galway)
- [Why Ireland is emerging as a hub for SaMD and EU health data innovation](https://www.healthcareittoday.com/2026/07/22/regulation-data-and-digital-health-why-ireland-is-emerging-as-a-hub-for-samd-and-eu-health-data-innovation/)
- [EU MDR & AI Act Compliance for AI Medical Devices — IntuitionLabs](https://intuitionlabs.ai/articles/ai-medical-device-compliance-eu-mdr-ai-act)
- [The EU Medical Device Shake-Up — Arnold & Porter](https://www.arnoldporter.com/en/perspectives/advisories/2026/02/the-eu-medical-device-shake-up)
- [AI in Clinical Evaluation Reports: Responsible Use Under EU MDR](https://www.celegence.com/responsible-ai-clinical-evaluation-reports-eu-mdr/)
- [AI-Assisted Triage in Post-Market Surveillance — MedTech Intelligence](https://medtechintelligence.com/feature_article/ai-assisted-triage-accelerating-post-market-surveillance-while-eliminating-reporting-blind-spots/)
- [AI-Driven Medical Device Vigilance Platform Market Report 2026](https://www.researchandmarkets.com/reports/6226393/ai-driven-medical-device-vigilance-platform)
- [Connect a Medical Device to an EHR: FHIR and HL7 Integration Guide — BioT](https://www.biot-med.com/resources/overcoming-challenges-in-integrating-cloud-powered-medical-devices-with-ehr-and-emr-systems)
- [Reality Check: The Aspirations of the EHDS — JMIR](https://www.jmir.org/2025/1/e76491)
- [Partner with Medtech Companies — Enterprise Ireland](https://www.enterprise-ireland.com/en/global/medtech)
- [Market access — Enterprise Ireland](https://www.enterprise-ireland.com/en/supports/market-access)
- [€7m funding for BioInnovate Ireland at University of Galway](https://stories.universityofgalway.ie/minister-higgins-announces-7m-funding-for-bioinnovate-ireland-at-university-of-galway/index.html)
- [BioInnovate programme puts fresh eyes on medtech innovation — Irish Times](https://www.irishtimes.com/business/bioinnovate-programme-puts-fresh-eyes-on-medtech-innovation-1.2567887)
