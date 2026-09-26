# Runtime parity och project hygiene

Steg 17 validerar de tre aktiverade runtimes mot samma canonical kontrakt:

- `chatgpt_chat`
- `chatgpt_custom`
- `claude_project`

Ingen runtime används som referensruntime. `scripts/runtime_parity.py` jämför i stället varje runtime mot canonical instruktion, runtimekontrakt och obligatoriskt Knowledge-stöd. Rapporten följer `schemas/runtime-parity.schema.json`.

## Parity-gates

Följande är blockerande om de saknas i någon aktiverad runtime:

- de fyra användarscenarierna,
- risk- och placeringshorisontgate,
- strategisk och taktisk allokering,
- verifiering mot Swedbank ISK,
- principen minsta rimliga förändring,
- guided workflow, terminal behavior och felåterhämtning,
- required webbresearch,
- required structured data,
- läsning av uppladdade filer/dokument.

Kodexekvering är `recommended`, inte ett obligatoriskt runtimekrav. Runtime-paketen bäddar därför inte in en exekveringsmotor; exakt matematik ska kunna verifieras med hostens tillgängliga beräkningsstöd när sådant finns.

## Hygiene

`scripts/project_hygiene.py --mode final` körs på canonical källträd före build. Genererade `build/` och `dist/` betraktas som regenererbara och ska inte behöva finnas i källträdet för att projektet ska vara komplett.

Steg 17 producerar:

- `docs/runtime-parity-report.json`
- `docs/runtime-parity-report.md`
- `docs/project-hygiene-report.json`

CI och release kör både final hygiene och runtime parity som blockerande kontroller.
