# ChatGPT Chat-runtime – valideringskontrakt

Chat-distributionen är v1:s portabla konversationspaket. Den ska kunna användas genom att ZIP-filen bifogas i en ChatGPT-konversation och anges som GPT-kontext.

## Obligatoriskt innehåll

- `START-HERE.md`
- `assistant/instructions.md`
- `assistant/runtime-contract.json`
- `assistant/policies/`
- scenario- och analysrelevant `knowledge/`
- `VERSION`
- `MANIFEST.json`

Chat-paketet får inte innehålla utvecklingsmaterial såsom `tests/`, `evals/`, `research/`, `.github/`, `build/` eller `dist/`.

## Kärnscenarier

Den kompilerade Chat-instruktionen måste själv kunna routa och styra samtliga fyra arbetslägen:

1. Analysera befintlig portfölj.
2. Skapa ny portfölj.
3. Hitta fond.
4. Ersätt fond.

Kritiska gates för risk/placeringshorisont, Swedbank-ISK-verifiering, datakvalitet, strategiaktualitet och matematisk kontroll ska finnas i instruktionen. Knowledge får ge detaljer och referenslogik men får inte vara enda platsen där kärnbeteendet finns.

## Runtimeförmågor

Chat-snapshoten ska bevara att webbresearch och strukturerad data är obligatoriska för full funktion. Kodexekvering är rekommenderad men inte ett krav för att paketet ska kunna ge säker partiell analys.

## Deterministisk validering

Kör efter build:

```bash
python3 scripts/validate_chat_runtime.py --build-dir build/chat
```

Validatorn kontrollerar paketstruktur, manifest/hashar, canonical kärnmarkörer, de fyra scenario-markörerna, runtimekontrakt och förbjudna utvecklingsfiler.
