# Portföljassistenten – utvecklingsplan

## Projektprofil

- **Projekt:** Portföljassistenten
- **Primärt användningsfall:** analys och beslutsstöd för fonder som kan köpas av privatkund via Swedbank ISK
- **Framtida utbyggnad:** fler banker och fondplattformar genom provider-/adaptermodell
- **Profil:** `workflow_research_heavy`
- **Modellrobusthet:** `guided`
- **Primära datakällor:** aktuell uppladdad Swedbank Investeringsstrategi, Swedbanks fondutbud, fondbolagens officiella fondinformation och faktablad, kompletterande verifierbara fondkällor
- **Aktiverade runtimes som standard:** ChatGPT Chat, ChatGPT Custom, Claude Projects
- **Bedömda men inte standardaktiverade i v1:** OpenCode, OpenAI Plugin

## Grundprinciper

1. GPT:n ska skilja mellan **strategisk allokering** och **taktisk allokering**.
2. Strategisk allokering ska främst härledas från placeringshorisont, risknivå och relevanta användarförutsättningar.
3. En uppladdad investeringsstrategi får användas som taktisk modifierare, inte som ensam grund för användarens risknivå.
4. Konkreta fondförslag i v1 ska som standard begränsas till fonder som kan verifieras som tillgängliga för Swedbank ISK.
5. Fondanalys ska så långt data medger använda faktisk exponering: tillgångsslag, geografiska regioner, risk, avgift och historisk utveckling.
6. För befintliga portföljer ska standardprincipen vara att **förändra så lite som möjligt** för att närma portföljen till målallokeringen.
7. Historisk avkastning får användas för jämförelse och förståelse, men ska inte ensam styra målallokering eller fondval.
8. Källor och datadatum ska redovisas tydligt, särskilt för föränderliga fonddata.
9. Swedbank-specifik logik ska hållas separat från den generiska portfölj- och fondmodellen så att fler banker kan läggas till senare.

## Kärnflöden

### A. Analysera befintlig portfölj

Användaren anger befintliga fonder och procentuell fördelning och kan bifoga aktuell investeringsstrategi. GPT:n ska:

- verifiera eller efterfråga risknivå och placeringshorisont när de behövs för ett konkret förslag,
- identifiera fonderna och aktuell fonddata,
- beräkna portföljens faktiska exponering mot tillgångsslag och regioner,
- härleda strategisk målallokering,
- applicera relevant taktisk syn från investeringsstrategin,
- identifiera avvikelser,
- föreslå begränsade förändringar med kategorierna Behåll, Öka, Minska, Ersätt och Komplettera,
- förklara vilket problem varje föreslagen förändring löser.

### B. Skapa ny portfölj

Användaren efterfrågar en portfölj och kan bifoga investeringsstrategi. GPT:n ska:

- säkerställa risknivå och placeringshorisont,
- skapa strategisk tillgångsallokering,
- skapa strategisk regionallokering inom aktiedelen,
- applicera taktiska avvikelser från aktuell investeringsstrategi inom definierade ramar,
- identifiera fonder i Swedbanks ISK-utbud som ger önskad exponering,
- föreslå procentuell fördelning mellan fonderna,
- redovisa faktisk beräknad exponering för den föreslagna portföljen.

### C. Hitta fond i en kategori

Användaren efterfrågar exempelvis Sverige, USA, kort ränta, lång ränta, Investment Grade eller High Yield. GPT:n ska:

- verifiera aktuell tillgänglighet hos Swedbank,
- ta fram relevanta kandidater,
- jämföra exponering, avgift, risk, historik, förvaltningsstil och relevanta skillnader,
- använda investeringsstrategi som kompletterande signal om sådan finns,
- presentera ett litet antal tydliga kandidater med styrkor och svagheter utan att låta historisk vinnare automatiskt bli standardval.

### D. Ersätt fond

Användaren anger en fond som ska bytas ut. GPT:n ska:

- identifiera vilken funktion fonden har i portföljen,
- identifiera faktisk geografisk och tillgångsmässig exponering,
- hitta kandidater i Swedbanks ISK-utbud som kan fylla samma funktion eller lösa ett uttryckligt problem bättre,
- jämföra kostnad, risk, exponering, historik och överlapp med andra innehav,
- redovisa konsekvensen för portföljen om fonden ersätts.

## Utvecklingssteg

### Steg 1 – Skapa canonical projektgrund

**Mål:** skapa första kompletta projektstrukturen och göra analysbesluten beständiga.

**Utdata:**
- `README.md`
- `PROJECT.md`
- `STATUS.md`
- `gpt-project.yaml`
- `project-status.yaml`
- `docs/development-plan.md`
- canonical instruktion med kärnkontrakt
- initiala capability-, artifact-, tool- och runtimekontrakt

**Validering:**
- projektstruktur följer GPT Byggaren 1.5.0,
- samtliga registrerade runtimes finns i runtimebedömningen,
- aktiverade build-targets överensstämmer med runtimebeslut,
- Swedbank är provider/adaptor och inte hårdkodad i kärnmodellen.

**Klart när:** projektet kan byggas till en komplett projekt-ZIP och status anger nästa steg entydigt.

### Steg 2 – Definiera portfölj- och fonddatamodell

**Mål:** skapa en plattformsneutral intern representation för portfölj, fond och exponering.

**Utdata:**
- schema/modell för fondidentitet och provider-tillgänglighet,
- tillgångsallokering,
- geografisk allokering,
- risk och avgifter,
- historisk utveckling med period och datadatum,
- portföljinnehav och målvikter,
- stöd för fond-i-fond/blandfond där källorna medger genomlysning.

**Tester:** representera minst global aktiefond, regional fond, räntefond, kreditfond och blandfond.

**Klart när:** samma modell kan beskriva både Swedbank-fond och framtida extern provider utan ändring av kärnschemat.

### Steg 3 – Implementera käll- och evidensregler

**Mål:** säkerställa att aktuell fonddata kan hittas, verifieras och citeras konsekvent.

**Utdata:**
- källhierarki,
- regler för Swedbanks fondutbud,
- regler för officiella fondbolagskällor/faktablad,
- regler för kompletterande källor,
- `as_of_date`/datadatum,
- hantering av saknade eller motstridiga uppgifter,
- regel att en fond inte får presenteras som verifierad Swedbank-ISK-kandidat utan tillräckligt stöd.

**Tester:** fall med aktuell data, gammal data, motstridiga källor och ej verifierad Swedbank-tillgänglighet.

**Klart när:** fondfakta kan härledas med tydlig provenance och osäkerhet.

### Steg 4 – Implementera investeringsstrategi-tolkning

**Mål:** tolka uppladdade Swedbank Investeringsstrategier till strukturerade taktiska signaler.

**Utdata:**
- identifiering av strategidatum,
- över-/neutral-/undervikt per tillgångsslag,
- regionviktning,
- relevanta subpreferenser såsom kort/lång ränta och IG/HY,
- produktförslag separerade från själva allokeringssignalen,
- kontroll att neutralvikt inte feltolkas som lika vikt.

**Tester:** september 2026-strategin som referensfall samt syntetiska över-/underviktsfall.

**Klart när:** strategin kan sammanfattas till en reproducerbar taktisk signalmodell.

### Steg 5 – Definiera strategisk målallokering och riskdialog

**Mål:** skapa regler för hur risk och placeringshorisont påverkar långsiktig tillgångsfördelning.

**Utdata:**
- minsta nödvändiga frågor till användaren,
- regler för när risk/horizont måste bekräftas,
- intervall eller profiler för strategisk allokering,
- principer för strategisk regionallokering,
- tydlig avgränsning mellan långsiktig riskprofil och taktisk månadssyn.

**Tester:** kort/lång horisont, låg/hög risk samt ofullständiga användaruppgifter.

**Klart när:** samma användarprofil ger konsekvent strategisk målallokering före taktiska justeringar.

### Steg 6 – Implementera taktisk justeringsmotor

**Mål:** kombinera strategisk målallokering med investeringsstrategins taktiska signaler utan att riskprofilen åsidosätts.

**Utdata:**
- definierade justeringsramar för över-/undervikt,
- gränser för maximal taktisk avvikelse,
- regler för neutralvikt,
- stöd för hierarkiska signaler: aktier/räntor/krediter → regioner/subkategorier.

**Tester:** neutral regionallokering, aktieövervikt, ränteundervikt, HY-övervikt och kombinationer.

**Klart när:** samma indata ger deterministiskt förklarbar målallokering och justeringarna håller sig inom riskramen.

### Steg 7 – Implementera look-through-portföljanalys

**Mål:** beräkna faktisk portföljexponering från flera fonder.

**Utdata:**
- aggregering av tillgångsslag,
- aggregering av regioner,
- hantering av blandfonder och globalfonder,
- identifiering av överlapp och koncentration,
- jämförelse mot strategisk och taktisk målallokering.

**Tester:** portfölj med globalfond + USA + Sverige + blandfond och kontroll av dubbel USA-exponering.

**Klart när:** GPT:n kan skilja fondvikter från faktisk underliggande exponering.

### Steg 8 – Implementera scenario A: analysera befintlig portfölj

**Mål:** skapa komplett arbetsflöde för analys och begränsad rebalansering.

**Utdata:**
- inmatningsdialog,
- portföljdiagnos,
- avvikelseanalys,
- Behåll/Öka/Minska/Ersätt/Komplettera,
- procentuella förändringsförslag,
- före-/efter-exponering.

**Tester:** redan välbalanserad portfölj, tydligt sned portfölj, saknad risknivå och fond med otillräcklig data.

**Klart när:** GPT:n som standard föreslår minsta rimliga förändring i stället för total omläggning.

### Steg 9 – Implementera scenario B: skapa ny portfölj

**Mål:** skapa portfölj från riskprofil, placeringshorisont och aktuell strategi.

**Utdata:**
- målallokering,
- fondurval ur verifierat Swedbank-utbud,
- procentuell fondfördelning,
- beräknad faktisk exponering,
- motivering och källor.

**Tester:** flera riskprofiler och en strategi med både neutrala och aktiva taktiska signaler.

**Klart när:** summan av fondvikter är 100 %, målallokeringen förklaras och varje föreslagen fond är verifierad eller uttryckligen markerad som osäker.

### Steg 10 – Implementera scenario C: hitta fond

**Mål:** screena och jämföra fonder inom efterfrågad kategori.

**Utdata:**
- kategorimatchning,
- kandidatlista,
- jämförelse av kostnad, exponering, risk, historik och förvaltningsstil,
- tydlig redovisning av varför kandidater skiljer sig.

**Tester:** Sverige, USA, kort ränta, lång ränta och High Yield.

**Klart när:** kandidaten väljs utifrån flera relevanta dimensioner och inte enbart historisk avkastning.

### Steg 11 – Implementera scenario D: ersätt fond

**Mål:** hitta ersättare som bevarar eller avsiktligt förbättrar fondens portföljfunktion.

**Utdata:**
- funktionsanalys av befintlig fond,
- ersättningskandidater,
- jämförelse före/efter,
- portföljpåverkan och överlapp.

**Tester:** dyr aktiv fond → billigare alternativ, fond som saknar direkt motsvarighet och fondbyte som oavsiktligt skulle ändra regionexponering.

**Klart när:** GPT:n visar konsekvensen av bytet för hela portföljen, inte bara fond-för-fond-jämförelsen.

### Steg 12 – Canonical instruktion och guided workflow

**Mål:** konsolidera kärnbeteendet så att det fungerar robust även i enklare modeller.

**Utdata:**
- kort operativ kärna,
- regler för val av scenario,
- gates för datakvalitet, risk/horizont och verifierad tillgänglighet,
- terminal behavior och felåterhämtning,
- begränsat antal obligatoriska filhopp.

**Validering:** instruction-adherence och model-compatibility-evals.

**Klart när:** kärnflödena inte är beroende av att modellen hittar kritiska regler i Knowledge.

### Steg 13 – Tester och evals

**Mål:** verifiera beteende, beräkningar och källhantering över samtliga kärnscenarier.

**Utdata:**
- evalfall för de fyra arbetslägena,
- multi-turn retention,
- felåterhämtning,
- saknade data,
- motstridiga data,
- felaktigt fondnamn,
- gammal investeringsstrategi,
- neutralviktstolkning,
- matematisk kontroll av procentvikter.

**Klart när:** blockerande evals passerar och kända begränsningar är dokumenterade.

### Steg 14 – ChatGPT Chat-distribution

**Mål:** bygga portabel Chat ZIP från canonical kontrakt.

**Utdata:** Chat ZIP, START-HERE och runtimekontrakt.

**Klart när:** distributionen validerar och kärnscenarierna fungerar i Chat.

### Steg 15 – ChatGPT Custom-distribution

**Mål:** kompilera projektet till Custom GPT inom plattformens begränsningar.

**Utdata:** instruktion, Knowledge-paket och installations-/valideringsunderlag.

**Klart när:** kritiskt beteende finns kvar efter kompilering och valideringen passerar.

### Steg 16 – Claude Projects-distribution

**Mål:** skapa Claude-portabel distribution från samma canonical kontrakt.

**Utdata:** Claude-projektpaket och dokumenterade skillnader.

**Klart när:** kärnscenarierna fungerar och runtimebegränsningar är dokumenterade.

### Steg 17 – Runtime parity och project hygiene

**Mål:** säkerställa att aktiverade runtimes representerar samma kärnbeteende och att projektet är rent.

**Utdata:** runtime-parity-rapport och hygiene-rapport.

**Klart när:** inga blockerande skillnader eller hygiene-fel återstår.

### Steg 18 – CI, release och release readiness

**Mål:** automatisera validering och bygga releaserbara artefakter.

**Utdata:**
- GitHub Actions CI,
- release-workflow,
- versionering från release-tag,
- fullständig projekt-ZIP,
- aktiverade runtime-distributioner,
- release-readiness-rapport.

**Klart när:** lint, tester, builds, distributionsvalidering, hygiene och runtime parity passerar utan blockerare.

## Framtida expansionsspår

Dessa ingår inte i v1-kärnan men arkitekturen ska möjliggöra dem:

- fler banker och fondplattformar,
- bank-/provider-specifika adapters,
- fler tillgångsslag,
- sektorallokering,
- valutarisksanalys,
- automatiserad uppdatering av fonduniversum via API eller strukturerad källa när sådan är tillgänglig,
- jämförelse mellan samma målportfölj hos flera banker.

## Nästa rekommenderade steg

**Steg 1 – Skapa canonical projektgrund.** Detta blir första genomförandesteget och ska även skapa den första kompletta projekt-ZIP:en med denna plan som `docs/development-plan.md`.
