# Portföljassistenten

Portföljassistenten är ett GPT-projekt för analys och beslutsstöd kring fondportföljer, med första versionen inriktad på fonder som kan köpas av privatkund via Swedbank ISK.

Projektet är byggt med en plattformsneutral kärna. Swedbank behandlas som den första fondplattformen/provider och ska kunna kompletteras med fler banker och fondplattformar senare utan att kärnmodellen behöver skrivas om.

## Huvudfunktioner

- analysera en befintlig fondportfölj och föreslå begränsade justeringar,
- föreslå en ny portfölj utifrån risk och placeringshorisont,
- hitta och jämföra fonder inom en viss kategori,
- hitta lämpliga ersättare för en befintlig fond,
- använda en aktuell uppladdad investeringsstrategi som taktisk signal,
- analysera faktisk exponering mot tillgångsslag och geografiska regioner.

Se `PROJECT.md` för projektkontraktet och `docs/development-plan.md` för utvecklingsplanen.


## Utvecklingsstatus

Steg 17 är klart. De tre aktiverade runtimes har verifierad parity mot canonical kontrakt och project hygiene passerar. Nästa steg är steg 18: CI, release och release readiness.

## Runtimevalidering

Efter build kan ChatGPT-runtimes valideras deterministiskt med:

```bash
python scripts/validate_chat_runtime.py --build-dir build/chat
python scripts/validate_custom_gpt_runtime.py --build-dir build/custom-gpt
python scripts/validate_claude_runtime.py --build-dir build/claude
python scripts/runtime_parity.py --project-root . --check
```

Final project hygiene körs på rent källträd med:

```bash
python scripts/project_hygiene.py --project-root . --mode final
```
