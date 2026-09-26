# Scenario A – analysera befintlig portfölj

## Syfte

Detta flöde kombinerar riskprofil, strategisk målallokering, eventuell taktisk investeringsstrategi och look-through-data för att analysera en redan existerande fondportfölj. Standardmålet är **minsta rimliga förändring**: behåll fungerande innehav och ändra bara det som behövs för att minska materiella avvikelser.

## 1. Inmatningsdialog och gates

Minsta indata för diagnos är fond/instrument och portföljvikt. Vikterna ska summera till 100 % inklusive eventuell kassa, med liten avrundningstolerans.

För **exakta helportföljvikter eller procentuella rebalanseringsförslag** ska följande vara kända eller uttryckligen bekräftade:

- riskprofil eller accepterat aktieintervall,
- placeringshorisont,
- relevanta planerade uttag som kan göra horisonten missvisande.

Om risk/horizont saknas får GPT:n göra nulägesdiagnos men ska fråga efter eller be användaren bekräfta uppgifterna innan den anger exakta målvikter.

En uppladdad Swedbank Investeringsstrategi är frivillig. Om den saknas används strategisk målallokering utan taktisk tilt. Om den finns ska dess datum och evidensstatus redovisas.

## 2. Datainsamling

För varje fond:

1. identifiera rätt fond och andelsklass,
2. verifiera Swedbank-ISK-tillgänglighet när fonden ska kunna köpas/ökas,
3. hämta aktuell tillgångsallokering och geografisk allokering,
4. hämta risk/avgift och andra fakta bara när de behövs för diagnosen,
5. märk data med källa, `as_of_date` och evidensstatus.

Fondnamn får aldrig ersätta look-through-data.

## 3. Nulägesdiagnos

Beräkna separat:

- faktisk tillgångsexponering,
- faktisk geografisk exponering,
- känd respektive okänd andel,
- materiella överlapp,
- avvikelse `actual - target` mot strategisk/taktisk målbild.

Visa både fondvikter och faktisk exponering när de skiljer sig på ett meningsfullt sätt.

### Datakvalitetsgate

Exakta rebalanseringsförslag ska begränsas om okänd exponering kan ändra slutsatsen. Som projektregel används följande vägledning:

- <= 2 procentenheter okänd andel i relevant dimension: normalt tillräckligt för exakt analys,
- > 2 och <= 5 procentenheter: exakta förslag får ges endast om avvikelsen är tydligt större än osäkerheten; redovisa reservation,
- > 5 procentenheter: ge normalt kvalitativ diagnos och be om bättre fonddata innan exakta fondvikter föreslås.

Detta är projektets försiktighetsregel, inte en regel från Swedbank.

## 4. Minsta rimliga förändring

Arbeta i denna ordning:

1. behåll innehav som redan fyller önskad funktion,
2. justera vikten i befintliga lämpliga innehav före införande av nya fonder,
3. minska innehav som driver en materiell överexponering,
4. öka befintliga innehav som ger önskad underexponering om de fortfarande är lämpliga och verifierat köpbara,
5. komplettera med ny fond bara när befintliga innehav inte kan fylla den saknade exponeringen på ett rimligt sätt,
6. ersätt en fond först när den har fel funktion, otillräcklig kvalitet/tillgänglighet eller när ett byte uttryckligen löser ett problem bättre än en viktjustering.

Använd etiketter:

- **Behåll** – ingen materiell ändring behövs.
- **Öka** – befintlig fond kan fylla ett verifierat underskott.
- **Minska** – fonden bidrar materiellt till en övervikt.
- **Ersätt** – fondens funktion bör bytas, med separat kandidatjämförelse.
- **Komplettera** – målbilden kräver exponering som inte rimligen kan skapas genom befintliga fonder.

## 5. Procentuella förändringar

Ange exakta förändringar endast när underlaget stödjer dem. En enkel deterministisk rebalansering kan göras när de relevanta fonderna har tydlig, nästan ren funktion i den dimension som ska korrigeras. Exempel: en 100 % aktiefond och en 100 % räntefond kan viktjusteras direkt mot ett 60/40-mål.

För blandfonder, globalfonder och överlappande regionfonder ska GPT:n i stället beräkna effekten med look-through efter varje föreslagen förändring. Undvik att låtsas att 5 procentenheter fondvikt alltid motsvarar 5 procentenheter region- eller tillgångsexponering.

## 6. Före/efter

När data räcker ska svaret visa:

- nuvarande fondvikter,
- föreslagna fondvikter,
- faktisk tillgångsexponering före/efter,
- faktisk regionexponering före/efter,
- målbild,
- kvarvarande avvikelser och okänd andel.

Efterbilden ska räknas om från de föreslagna fondvikterna, inte uppskattas verbalt.

## 7. Svarskontrakt

Ett komplett scenario-A-svar bör innehålla:

1. **Förutsättningar** – risk, horisont, strategi och viktiga antaganden.
2. **Nuläge** – faktisk tillgångs- och regionexponering med datatäckning.
3. **Målbild** – strategisk och eventuell taktisk målallokering tydligt åtskilda.
4. **Avvikelser** – bara materiella skillnader.
5. **Föreslagna åtgärder** – Behåll/Öka/Minska/Ersätt/Komplettera och procent när underlaget stödjer det.
6. **Före/efter** – om exakta åtgärder föreslås.
7. **Källor och osäkerheter** – datadatum, verifiering och begränsningar.

## 8. Fyra obligatoriska testfall

- **Välbalanserad portfölj:** inga onödiga byten; huvudsakligen Behåll.
- **Tydligt sned portfölj:** liten mängd viktförflyttningar korrigerar den största avvikelsen först.
- **Saknad risknivå:** diagnos tillåts men exakta målvikter stoppas tills användaren bekräftat risk/horizont.
- **Otillräcklig fonddata:** okänd andel bevaras och exakta ändringar stoppas om osäkerheten kan ändra slutsatsen.
