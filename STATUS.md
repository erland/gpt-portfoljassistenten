# Status

## Klart

- Behovs- och lösningsanalys.
- Utvecklingsplan.
- Canonical projektgrund skapad.
- Runtimekandidater bedömda; ChatGPT Chat, ChatGPT Custom och Claude Projects aktiveras som standard i v1.
- Swedbank ISK är första provider, men kärnarkitekturen är provider-neutral.
- Canonical portfölj- och fonddatamodell definierad.
- Fondidentitet, provider-tillgänglighet, tillgångs- och geografisk allokering, risk, avgifter, historisk utveckling och provenance är modellerade.
- Look-through-stöd definierat för globalfond, regional fond, räntefond, kreditfond och blandfond/fond-i-fond.
- Källhierarki och evidensstatus definierade per faktatyp.
- Aktualitetsregler finns för tillgänglighet, allokering, avgifter/risk och historisk utveckling.
- Motstridiga och saknade uppgifter hanteras explicit utan tyst konfliktlösning eller gissningar.
- Verifierad Swedbank-ISK-kandidat kräver aktuell officiell Swedbank-evidens för tillgänglighet.
- Evidensmodell och testfall täcker aktuell, gammal, motstridig och ej verifierad data.
- Investeringsstrategi-tolkning implementerad som strukturerad taktisk signalmodell.
- Strategidatum, tillgångsslag, regioner, räntesegment och kreditsegment hålls hierarkiskt separerade.
- Neutralvikt tolkas relativt strategisk normalvikt och aldrig som lika vikt.
- Produktförslag och affärsförslag separeras från allokeringssignaler.
- September 2026-strategin finns som referensfixture tillsammans med syntetiskt aktivt regionfall.
- Strategisk målallokering och riskdialog definierad.
- Fyra provider-neutrala arbetsprofiler finns: Försiktig, Balanserad, Hög och Mycket hög, med reproducerbara defaultvikter och aktieintervall.
- Placeringshorisont används som kontrollsignal, inte automatisk riskmotor; kort horisont/närtida likviditetsbehov kan utlösa bekräftelsekrav.
- Strategisk regionbaslinje bygger på aktuell global marknadsviktad referens; exakta regionvikter hårdkodas inte och svensk home bias är ett separat användarval.
- Scheman och tester finns för investerarprofil och strategisk allokering.

## Nästa steg

**Projektplanen (steg 1–18) är genomförd. Nästa naturliga steg är första releasekandidaten/stabila releasen när projektet lagts i GitHub.**


## Steg 6 – taktisk justeringsmotor

Klart. Projektet har deterministiska regler för ±3 pp vid normal och ±5 pp vid tydlig/stark signal, explicit finansiering mellan huvudklasser, riskklippning, neutralvikt = 0 samt hierarkiska sleeve-justeringar för regioner, duration och IG/HY. Referensfallet september 2026 är testat mot balanserad 60/30/10.

**Nästa steg:** Steg 13 – bredda tester och evals.


## Steg 7 – look-through-portföljanalys

Klart. Projektet kan nu aggregera faktisk tillgångs- och regionexponering från flera fonder, bevara okänd andel vid partial/saknad data, identifiera överlapp och koncentrationsbidrag samt jämföra faktisk exponering mot målallokering. Referensfallet med globalfond + USA-fond + Sverige-fond + blandfond verifierar dubbel USA-exponering och partial coverage.

**Nästa steg:** Steg 13 – bredda tester och evals.


## Steg 8 – scenario A: analysera befintlig portfölj

Klart. Projektet har nu ett komplett scenario-A-flöde med viktvalidering, risk-/horisontgate, look-through-diagnos, datakvalitetsgate, Behåll/Öka/Minska/Ersätt/Komplettera-principer, konservativ exakt rebalansering när fondrollerna är tillräckligt rena samt omräknad före/efter-exponering. Fyra obligatoriska testfall plus invalid viktning är implementerade.

**Nästa steg:** Steg 13 – bredda tester och evals.


## Steg 9 – scenario B: skapa ny portfölj

Klart. Projektet kan nu skapa en ny portfölj från bekräftad profil och effektiv målallokering, översätta sleeves till transparenta byggblock, välja endast verifierade Swedbank-ISK-kandidater som huvudförslag, lämna olösta roller explicita och kontrollera faktisk top-level- och aktieregionexponering med look-through. Flera risk-/taktikfall samt unverified/missing-profile/invalid-target är testade.

**Nästa steg:** Steg 13 – bredda tester och evals.


## Steg 10 – scenario C: hitta fond

Klart. Projektet kan nu normalisera efterfrågad fondkategori till en exponeringsroll, screena faktisk look-through-exponering, kräva verifierad Swedbank-ISK-tillgänglighet för primärt köp-förslag och jämföra kandidater på datatäckning, avgift, risk, förvaltningsstil samt historik. Historisk avkastning är uttryckligen bakgrund och inte ensam rankinggrund. Testfall täcker Sverige, USA, kort ränta, lång ränta och High Yield samt unverified-kandidat med hög historisk avkastning.

**Nästa steg:** Steg 13 – bredda tester och evals.


## Steg 11 – scenario D: ersätt fond

Klart. Projektet identifierar den befintliga fondens faktiska funktion, kräver verifierad Swedbank-ISK-tillgänglighet för primär ersättare, simulerar byte på hela portföljen och redovisar tillgångs-/regiondrift och före/efter. Dyr aktiv Sverigefond → billigare likvärdig kandidat, ingen direkt motsvarighet och oavsiktlig regionförändring är testade.

**Nästa steg:** Steg 13 – bredda tester och evals.

## Steg 12 – canonical instruktion och guided workflow

Klart. Canonical instruktion innehåller nu explicit scenario-routing, gate-ordning för risk/horizont, verifierad Swedbank-ISK-tillgänglighet, datakvalitet, strategiaktualitet och matematik, samt terminal behavior och felåterhämtning. Kärnflödena är självbärande utan obligatoriska Knowledge-hopp. Modellkompatibilitets-evals har utökats med routing, datakvalitetsgate, källfel, minimal följdfråga och gammal investeringsstrategi.

**Nästa steg:** Steg 13 – bredda tester och evals för multi-turn, motstridiga data, felaktiga fondnamn och matematisk kontroll.


## Steg 13 – tester och evals

Klart. Model-compatibility-sviten omfattar nu multi-turn retention, motstridiga fonddata, otydliga fondnamn/andelsklasser, felaktiga portföljvikter och neutralviktstolkning utöver tidigare stale-strategi-, datakvalitets- och källfelsfall. Canonical instruktion bevarar bekräftad risk, horisont, portfölj och strategi mellan turer utan onödiga följdfrågor. Kända begränsningar dokumenteras i `docs/known-limitations.md`.

**Nästa steg:** Steg 14 – färdigställ och validera ChatGPT Chat-distributionen.


## Steg 14 – ChatGPT Chat-distribution

Klart. Chat ZIP har ett explicit runtimevalideringskontrakt och deterministisk validator för paketstruktur, manifest/hashintegritet, canonical kärnmarkörer, de fyra scenarierna, runtimeförmågor och scenario-Knowledge. Chat-paketet verifieras dessutom fritt från utvecklingsmaterial.

**Nästa steg:** Steg 15 – färdigställ och validera ChatGPT Custom-distributionen.

## Steg 15 – ChatGPT Custom GPT-distribution

Klart. Custom GPT-paketet har nu ett explicit Builder-valideringskontrakt och deterministisk validator för 8 000-teckensbudgeten, Knowledge-gränsen på 20 filer, compilation-report-konsistens, canonical kärnmarkörer, de fyra scenarierna, runtimeförmågor, Builder-installationsunderlag och manifest/hashintegritet. CI och release kör både Chat- och Custom GPT-runtimevalidering efter build.

**Nästa steg:** Steg 16 – färdigställ och validera Claude Projects-distributionen.



## Steg 16 – Claude Projects-distribution

Klart. Claude Projects-paketet valideras nu explicit mot canonical kärnbeteende, de fyra scenarierna, Knowledge-paketet, capability/runtime-kontraktet, dokumenterade runtimebegränsningar och manifest/hashintegritet. Distributionen är uttryckligen för Claude Projects och använder inte Claude Code-konventioner.

**Nästa steg:** Steg 17 – runtime parity och project hygiene.

## Steg 17 – runtime parity och project hygiene

Klart. De tre aktiverade runtimes (`chatgpt_chat`, `chatgpt_custom`, `claude_project`) jämförs deterministiskt mot canonical kontraktet. Alla kritiska behavior- och capability-krav är equivalent. Endast optional, host-beroende funktioner som kodexekvering och nedladdningsbar Markdown-artefakt markeras reduced. Final project hygiene passerar på rent källträd utan findings. CI och release kör nu både final hygiene och runtime parity.

**Nästa steg:** Steg 18 – CI, release och release readiness.


## Steg 18 – CI, release och release readiness

Klart. CI och GitHub Release-workflow kör nu hela blockerande valideringskedjan och en separat release-readiness-gate. Readiness-rapporten bedömer project ZIP och samtliga aktiverade runtime-distributioner och bifogas till GitHub Release tillsammans med checksums och delivery manifest.
