# Claude Projects-runtimevalidering

Claude-distributionen är avsedd för **vanlig Claude Projects-användning**, inte Claude Code.

`python scripts/validate_claude_runtime.py --build-dir build/claude` verifierar att den byggda distributionen behåller canonical kärnbeteende och att runtimebegränsningarna är tydligt dokumenterade.

Kontrollen omfattar:

- de fyra kärnscenarierna: analysera befintlig portfölj, skapa ny portfölj, hitta fond och ersätt fond,
- kritiska regler för risk/horizont, strategisk/taktisk allokering, Swedbank-ISK-verifiering, guided workflow, gates och felåterhämtning,
- komplett Knowledge-paket med scenario- och analysmoduler,
- runtimekontrakt med `runtime_id=claude_project`, required web och structured data,
- att Project Instructions och Project Knowledge används utan Claude Code-konventioner,
- att lokala scripts/kommandon inte felaktigt påstås vara inbyggda verktyg,
- att README dokumenterar skillnader kring webbsökning, kodexekvering och connectors,
- manifest och SHA-256-integritet,
- att utvecklingsfiler inte läcker in i runtimepaketet.

## Dokumenterade runtime-skillnader

Canonical beteende är detsamma som i ChatGPT-distributionerna, men faktisk verktygstillgång i Claude Projects beror på konto och projektinställningar. Webbsökning, kodexekvering och connectors kan därför behöva aktiveras eller ersättas med manuell källinhämtning. Runtimepaketet innehåller inte lokala körbara scripts och använder inte `CLAUDE.md`.
