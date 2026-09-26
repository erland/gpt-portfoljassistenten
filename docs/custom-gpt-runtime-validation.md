# ChatGPT Custom GPT-runtime – valideringskontrakt

Custom GPT-distributionen är Builder-paketet för Portföljassistenten. Den ska kunna installeras genom att instruktionen kopieras till GPT Builder och Knowledge-filerna laddas upp utan att kärnbeteende går förlorat i kompileringen.

## Obligatoriskt innehåll

- `builder/instructions.md`
- `builder/conversation-starters.md`
- `builder/capabilities.md`
- `builder/runtime-contract.json`
- `builder/compilation-report.json`
- `builder/knowledge-package/`
- `README.md`
- `COMPATIBILITY.md`
- `VERSION`
- `MANIFEST.json`

Paketet får inte innehålla utvecklingsmaterial som `tests/`, `evals/`, `.github/`, `build/` eller `dist/`.

## Instruktionsbudget och kärnbeteende

Den kompilerade Builder-instruktionen får vara högst 8 000 tecken. Samtliga canonical kärnmarkörer och de fyra arbetslägena ska finnas direkt i instruktionen. Knowledge får fördjupa analysen men får inte vara enda platsen för blockerande gates eller scenario-routing.

De fyra arbetslägena är:

1. Analysera befintlig portfölj.
2. Skapa ny portfölj.
3. Hitta fond.
4. Ersätt fond.

## Knowledge-budget

Custom GPT-paketet får innehålla högst 20 Knowledge-filer. V1 kräver att data-, evidens-, strategi-, allokerings-, look-through- och samtliga fyra scenariofiler finns med. `compilation-report.json` ska exakt motsvara de filer som faktiskt ligger i paketet.

## Runtimeförmågor

`runtime-contract.json` ska bevara webbresearch och strukturerad data som obligatoriska för full funktion. `capabilities.md` ska därför instruera Builder-användaren att aktivera webbsökning. Kodexekvering/dataanalys är rekommenderad när den runtimefunktionen finns tillgänglig.

## Deterministisk validering

Kör efter build:

```bash
python3 scripts/validate_custom_gpt_runtime.py --build-dir build/custom-gpt
```

Validatorn kontrollerar teckenbudget, Knowledge-budget, compilation report, scenario- och kärnmarkörer, runtimekontrakt, Builder-installationsunderlag, manifest/hashar och förbjudna utvecklingsfiler.
