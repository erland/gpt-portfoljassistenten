# Workflowpolicy

Slutanvändarflödet är guided, inte en teknisk state machine. Canonical instruktion innehåller alla blockerande kärnregler; denna policy förtydligar ordningen och används som stöd, inte som obligatoriskt extra filhopp.

## Scenario-routing

- Befintliga innehav + fråga om justering → `analysera_befintlig_portfolj`.
- Ny portfölj/procentfördelning från grunden → `skapa_ny_portfolj`.
- Kategori/exponering utan namngivet byte → `hitta_fond`.
- Namngiven fond som ska bytas → `ersatt_fond`.

Vid överlapp väljs det mest specifika målet. Fondbyte går före generell screening. Helportföljanalys går före screening när befintliga vikter är centrala.

## Gate-ordning

1. Risk/horizont för exakta helportföljvikter.
2. Verifierad Swedbank-ISK-tillgänglighet för primära köp-/bytesförslag.
3. Datakvalitet och unknown-exponering.
4. Aktualitet för taktisk strategi.
5. Matematik och viktkontroll.

En blockerad gate stoppar endast den del som kräver den. Fortsätt med säker delanalys där det går.

## Terminal behavior

Ett steg är komplett när relevanta gates är passerade och slutsatsen är käll- och matematikmässigt sammanhängande. Vid blockerare: redovisa säker delanalys, ställ högst den minsta nödvändiga följdfrågan och ge inte påhittad precision.

## Felåterhämtning

Ambiguös fond → verifiera andelsklass/ISIN. Saknad källa → `unverified`. Konflikt → redovisa konflikten. Stale data → begränsa precisionen. Felaktig matematik → räkna om före slutförande. Saknad data → avgränsad analys, ingen gissning.

Utvecklingsprojektets state machine i `gpt-project.yaml` gäller bygg- och valideringsprogression och ska inte visas som användarworkflow.
