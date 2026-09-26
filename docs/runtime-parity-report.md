# Runtime parity – Portföljassistenten

## Sammanfattning

| Runtime | Nivå | Viktad täckning | Release |
|---|---|---:|---|
| chatgpt_chat | full | 98.9% | publish |
| chatgpt_custom | full | 98.9% | publish |
| claude_project | full | 98.9% | publish |

## Requirement-matris

| Krav | Kritikalitet | chatgpt_chat | chatgpt_custom | claude_project |
|---|---|---|---|---|
| Analysera befintlig portfölj | critical | equivalent | equivalent | equivalent |
| Skapa ny portfölj | critical | equivalent | equivalent | equivalent |
| Hitta fond | critical | equivalent | equivalent | equivalent |
| Ersätt fond | critical | equivalent | equivalent | equivalent |
| Risk och placeringshorisont | critical | equivalent | equivalent | equivalent |
| Strategisk allokering | critical | equivalent | equivalent | equivalent |
| Taktisk allokering | critical | equivalent | equivalent | equivalent |
| Verifiera Swedbank ISK | critical | equivalent | equivalent | equivalent |
| Minsta rimliga förändring | critical | equivalent | equivalent | equivalent |
| Guided workflow | critical | equivalent | equivalent | equivalent |
| Gates före konkreta förslag | critical | equivalent | equivalent | equivalent |
| Terminal behavior | critical | equivalent | equivalent | equivalent |
| Felåterhämtning | critical | equivalent | equivalent | equivalent |
| Kunskapsstöd: source-evidence-rules.md | important | equivalent | equivalent | equivalent |
| Kunskapsstöd: look-through-portfolio-analysis.md | important | equivalent | equivalent | equivalent |
| Kunskapsstöd: investment-strategy-interpretation.md | important | equivalent | equivalent | equivalent |
| Aktuell webbresearch | critical | equivalent | equivalent | equivalent |
| Strukturerad fond- och portföljdata | critical | equivalent | equivalent | equivalent |
| Läsning av uppladdade filer/dokument | critical | equivalent | equivalent | equivalent |
| Kodexekvering för exakt matematik | optional | reduced | reduced | reduced |
| Portfölj-/fondanalys som Markdown-artefakt | optional | reduced | reduced | reduced |
| Ephemeral konversationsstate med återanvändning mellan turer | important | equivalent | equivalent | equivalent |
| Obligatoriska deklarerade runtime-tools | optional | not_applicable | not_applicable | not_applicable |

## Reducerade krav

- **chatgpt_chat – Kodexekvering för exakt matematik:** Rekommenderad för exakt matematik men exekveringsmotor är host-/kontoberoende och ingår inte i paketet.
- **chatgpt_custom – Kodexekvering för exakt matematik:** Rekommenderad för exakt matematik men exekveringsmotor är host-/kontoberoende och ingår inte i paketet.
- **claude_project – Kodexekvering för exakt matematik:** Rekommenderad för exakt matematik men exekveringsmotor är host-/kontoberoende och ingår inte i paketet.
- **chatgpt_chat – Portfölj-/fondanalys som Markdown-artefakt:** Analysen kan alltid levereras som Markdown; nedladdningsbar fil beror på hostens fil-/artifact-stöd.
- **chatgpt_custom – Portfölj-/fondanalys som Markdown-artefakt:** Analysen kan alltid levereras som Markdown; nedladdningsbar fil beror på hostens fil-/artifact-stöd.
- **claude_project – Portfölj-/fondanalys som Markdown-artefakt:** Analysen kan alltid levereras som Markdown; nedladdningsbar fil beror på hostens fil-/artifact-stöd.

## Saknade krav

Inga blockerande eller saknade krav.

## Slutsats

De tre aktiverade runtimes bevarar samma kritiska kärnbeteende. Skillnaderna är begränsade till optional/host-beroende funktioner och blockerar inte release.
