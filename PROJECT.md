# Projektkontrakt – Portföljassistenten

## Syfte

Portföljassistenten ska hjälpa användaren att fatta mer informerade beslut om fondportföljer. Version 1 fokuserar på Swedbanks ISK-fondutbud men arkitekturen ska stödja framtida providers.

## Arbetslägen

1. **Analysera portfölj** – analysera nuvarande fondvikter och faktisk exponering, jämför mot målallokering och föreslå minsta rimliga förändring.
2. **Skapa portfölj** – skapa ett förslag utifrån risk, placeringshorisont och eventuell aktuell investeringsstrategi.
3. **Hitta fond** – screena kandidater i en efterfrågad kategori och jämför dem på flera relevanta dimensioner.
4. **Ersätt fond** – identifiera fondens portföljfunktion och hitta kandidater som kan fylla samma eller avsiktligt förbättrad funktion.

## Arkitekturprincip

Kärnan ska vara provider-neutral. Swedbank-specifik tillgänglighet, investeringsstrategi och produktinformation ska behandlas som providerdata/adaptrar och inte hårdkodas i den generiska portföljmodellen.

## Analysprincip

Strategisk allokering härleds från användarens risk, placeringshorisont och relevanta förutsättningar. En aktuell investeringsstrategi används som en begränsad taktisk modifierare. Fondvalet sker först efter att önskad exponering har identifierats.

## Källprincip

Aktuella fondfakta och fondtillgänglighet ska verifieras med aktuella källor. Officiella källor prioriteras och datadatum ska redovisas när uppgifterna är föränderliga.

## Canonical datamodell

Den provider-neutrala domänmodellen dokumenteras i `knowledge/portfolio-data-model.md` och formaliseras i `schemas/fund.schema.json` samt `schemas/portfolio.schema.json`. Föränderlig fonddata lagras som daterade snapshots med provenance. Fond-i-fond och blandfonder stöder full, partiell eller saknad look-through med explicit täckningsgrad.

## Aktuell status

Steg 18 är klart. Hela utvecklingsplanen är genomförd: CI, GitHub Release, versionering från release-tag och release-readiness-gate finns på plats och alla aktiverade runtimes ingår i releasebedömningen.


## Investeringsstrategi-tolkning

Swedbanks månadsvisa investeringsstrategi normaliseras till ett separat taktiskt signalobjekt. Signalerna är hierarkiska och skiljs från produkt- och affärsförslag. Referensfallet september 2026 finns i `tests/fixtures/investment-strategy/september-2026.yaml` och reglerna i `knowledge/investment-strategy-interpretation.md`.

## Strategisk målallokering och riskdialog

Den strategiska ramen definieras i `knowledge/strategic-allocation-and-risk-dialogue.md`. För helportföljförslag krävs bekräftad riskprofil och placeringshorisont. Projektet har fyra reproducerbara arbetsprofiler med explicita standardvikter, medan placeringshorisonten används som kontrollsignal och inte som automatisk riskökare. Strategiska regionvikter ska hämtas från en aktuell global marknadsviktad referens och får inte hårdkodas; svensk home bias är ett separat användarval.


## Taktisk justeringsmotor

Reglerna finns i `knowledge/tactical-adjustment-engine.md` och formaliseras i `schemas/tactical-allocation.schema.json`. Normal över-/undervikt ger som projektregel ±3 procentenheter och uttryckligen tydlig/stark signal ±5 procentenheter. Huvudklassjusteringar måste vara finansierade och klipps mot riskprofilens intervall. Underpreferenser för regioner, duration och kreditkvalitet hålls inom respektive sleeve. September 2026 används som referensfall: balanserad strategisk 60/30/10 blir 65/25/10 när tydlig aktieövervikt finansieras av räntor och riskramen tillåter det. Detta är projektets egen översättningsregel, inte en publicerad exakt Swedbank-vikt.

## Look-through-portföljanalys

Reglerna finns i `knowledge/look-through-portfolio-analysis.md` och den deterministiska referensimplementationen i `scripts/lib/look_through.py`. Analysen aggregerar fondvikt × verifierad exponering för tillgångsslag och geografi, behåller okänd andel explicit, identifierar överlapp och kan jämföra faktisk exponering mot målvikter. Partial look-through normaliseras aldrig bort.

- Scenario A för befintlig portfölj är implementerat med risk-/datagates, minsta rimliga förändring och beräknad före/efter-exponering.


## Scenario B – skapa ny portfölj

Nyportföljflödet finns i `knowledge/new-portfolio-construction.md` och `scripts/lib/new_portfolio.py`. Det kräver bekräftad risk/horizont för exakta vikter, bygger hierarkiskt från effektiv målallokering, använder verifierade Swedbank-ISK-byggblock, lämnar saknade roller explicita och räknar om faktisk look-through efter fondval.


## Scenario C – hitta fond

Fondscreening finns i `knowledge/fund-search-and-comparison.md` och `scripts/lib/fund_search.py`. Kandidater matchas mot faktisk exponering och verifierad Swedbank-ISK-tillgänglighet och jämförs på datatäckning, avgift, risk, förvaltningsstil och historik. Historisk avkastning visas som bakgrund men är inte ensam rankinggrund.


## Scenario D – ersätt fond

Ersättningsflödet finns i `knowledge/fund-replacement.md` och `scripts/lib/fund_replacement.py`. Det identifierar först den befintliga fondens faktiska portföljfunktion, screenar verifierade Swedbank-ISK-kandidater, simulerar bytet med oförändrad fondvikt och jämför faktisk tillgångs- och regionexponering före/efter. Kandidater som oavsiktligt ändrar portföljens funktion eller regionexponering nedprioriteras. Blandade fonder utan dominant funktion ger `no_direct_equivalent` i stället för en påtvingad en-fond-mot-en-fond-ersättare.

## Guided workflow

Canonical instruktion är självbärande för de fyra slutanvändarscenarierna och innehåller scenario-routing, blockerande gates, terminal behavior och felåterhämtning. Runtimepolicyn är endast stödjande; kritiskt beteende får inte kräva att modellen hittar en regel i Knowledge. Vid blockerad gate ska säker delanalys levereras och endast minsta nödvändiga följdfråga ställas.


## Tester och evals

Steg 13 har utökat model-compatibility-sviten till minst 14 blockerande scenarier. Den täcker multi-turn retention, källkonflikter, otydliga fondnamn, gammal strategi, neutralvikt, saknade data och matematisk kontroll. Kända begränsningar finns i `docs/known-limitations.md`.

- Chat runtime-validering: `scripts/validate_chat_runtime.py` och `docs/chat-runtime-validation.md`.
- Custom GPT runtime-validering: `scripts/validate_custom_gpt_runtime.py` och `docs/custom-gpt-runtime-validation.md`.


## Runtime parity och hygiene

De aktiverade runtimes jämförs mot canonical kontraktet genom `scripts/runtime_parity.py`. Rapporten finns i `docs/runtime-parity-report.json` och `.md`. Project hygiene körs i final-läge före build och rapporteras i `docs/project-hygiene-report.json`. CI och release blockerar på kritiska parity-gap eller hygiene-blockerare.


## Release readiness

Den slutliga releasen valideras med `scripts/release_readiness.py`. Rapporten skrivs som både JSON och Markdown och GitHub Release-workflow publicerar den tillsammans med projekt-ZIP, runtime-ZIP:ar, checksums och delivery manifest.
