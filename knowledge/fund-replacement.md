# Scenario D – ersätt fond

## Syfte

Scenario D används när användaren vill byta ut en befintlig fond. Målet är inte att hitta en fond som bara ser likadan ut i namn eller kategori, utan att först identifiera vilken funktion fonden faktiskt fyller och därefter bedöma ersättare utifrån effekten på hela portföljen.

## Arbetsgång

1. Identifiera den befintliga fondens funktion från aktuell faktisk exponering, inte från fondnamnet. Exempel är `equity_region:sweden`, `equity_region:usa`, `money_market_short`, `bonds_long`, `investment_grade` och `high_yield`.
2. Om fonden har en blandad eller flerdimensionell funktion utan tydlig direkt motsvarighet ska detta sägas uttryckligen. Tvinga inte fram en en-fond-mot-en-fond-ersättare.
3. Verifiera att primära ersättningskandidater är tillgängliga för privatkund på Swedbank ISK enligt källreglerna.
4. Jämför kandidater på funktionsmatchning, datatäckning, avgift, risk, förvaltningsstil och historik. Historisk avkastning är bakgrund och får inte ensam styra urvalet.
5. Om portföljens övriga innehav är kända: simulera bytet med samma fondvikt och räkna om faktisk tillgångs- och regionexponering före/efter.
6. Redovisa förändrad överlappning och materiella förändringar i portföljexponering. En kandidat som oavsiktligt ändrar region eller tillgångsslag ska nedprioriteras även om fonden i övrigt verkar attraktiv.
7. Vid tydligt önskemål om att ändra funktionen, till exempel från aktiv Sverigefond till global indexfond, får förändringen göras men ska beskrivas som en avsiktlig allokeringsförändring, inte som en likvärdig ersättning.

## Standardordning för ersättningskandidater

Utan särskilda användarönskemål:

1. verifierad Swedbank-ISK-tillgänglighet,
2. bevarad faktisk fondfunktion,
3. minsta oavsiktliga portföljdrift i tillgångsslag och regioner,
4. datatäckning och aktualitet,
5. rimlig risklikhet,
6. lägre löpande avgift när kandidater i övrigt är jämförbara,
7. deterministisk tie-break.

## Portföljpåverkan

När portföljen är känd ska analysen minst visa:

- fondens vikt före och efter,
- faktisk tillgångsallokering före och efter,
- faktisk geografisk allokering före och efter,
- största förändringar i procentenheter,
- överlapp som tillkommer eller försvinner,
- okänd exponering och datatäckning.

En ersättare bör normalt inte kallas funktionsbevarande om den skapar en materiell oavsiktlig förändring i region- eller tillgångsexponering.

## Ingen direkt motsvarighet

Om den befintliga fonden är en blandfond, fond-i-fond eller har en unik kombination av exponeringar kan bästa lösningen vara två eller flera byggblock. V1 ska då returnera `no_direct_equivalent` och beskriva vilka funktioner som måste återskapas, snarare än att låtsas att en svag enskild kandidat är likvärdig.

## Svar

Visa först fondens identifierade funktion. Presentera därefter en kort kandidatjämförelse med fond, verifierad tillgänglighet, funktionsmatchning, avgift, risk och beräknad portföljdrift. För en vald kandidat ska före/efter-effekten för hela portföljen redovisas. Förklara varför ett billigare alternativ kan vara rimligt och varför en kandidat med större portföljdrift kan vara olämplig trots andra styrkor.
