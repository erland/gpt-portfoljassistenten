# Scenario C – hitta och jämför fond

## Syfte

Scenario C används när användaren efterfrågar en fond inom en bestämd funktion eller kategori, till exempel Sverige, USA, kort ränta, lång ränta, Investment Grade eller High Yield. V1 ska i första hand screena fonder som är verifierat tillgängliga för privatkund på Swedbank ISK.

## Arbetsgång

1. Normalisera användarens önskemål till en fondroll, exempelvis `equity_region:sweden`, `equity_region:usa`, `money_market_short`, `bonds_long`, `investment_grade` eller `high_yield`.
2. Verifiera plattformstillgänglighet. En kandidat får vara primärt köp-förslag bara när tillgängligheten är verifierad enligt källreglerna.
3. Kontrollera faktisk exponering med aktuell look-through. Fondnamn eller marknadsföringskategori räcker inte som bevis på exponering.
4. Jämför flera relevanta dimensioner: exponeringsmatchning, datatäckning/aktualitet, löpande avgift, riskklass, aktiv/index/passiv förvaltning samt historisk utveckling.
5. Historisk utveckling är bakgrundsinformation och får aldrig ensam avgöra rangordningen.
6. Om användaren uttrycker en preferens, exempelvis indexnära, låg avgift eller viss risknivå, får den preferensen påverka urvalet transparent.
7. Presentera ett litet shortlist-urval och förklara skillnaderna. Ange när ett alternativ passar bättre än ett annat i stället för att låtsas att en fond är universellt bäst.

## Standardordning för screening

Utan särskilda användarpreferenser används följande ordning:

1. verifierad Swedbank-ISK-tillgänglighet,
2. faktisk matchning mot efterfrågad exponering,
3. täckningsgrad och aktualitet i look-through-data,
4. uttrycklig användarpreferens för förvaltningsstil eller risk,
5. lägre löpande avgift när kandidater i övrigt är jämförbara,
6. deterministisk tie-break.

Historisk avkastning visas för relevanta perioder där jämförbar data finns men är inte en rankingnyckel i standardordningen.

## Kategorier i v1

- Sverigeaktier: `equity_region:sweden`
- USA-aktier: `equity_region:usa`
- Kort ränta/penningmarknad: `money_market_short`
- Lång ränta/obligationer: `bonds_long`
- Investment Grade-krediter: `investment_grade`
- High Yield-krediter: `high_yield`

Arkitekturen är provider-neutral och kan utökas med fler kategorier och banker senare.

## Investeringsstrategins roll

En aktuell uppladdad Swedbank Investeringsstrategi kan ge kontext om huruvida kategorin är över-, neutral- eller underviktad och om det finns produktförslag. Den ändrar inte i sig fakta om fondens avgift, risk eller faktiska exponering och får inte ersätta verifiering av fondens aktuella ISK-tillgänglighet.

## Svar

Använd tabell när flera kandidater jämförs. Minimikolumner är fond, verifierad tillgänglighet, exponeringsmatchning, avgift, risk och förvaltningsstil. Lägg till historik när jämförbara perioder finns. Avsluta med en kort förklaring av vilka trade-offs som skiljer kandidaterna och vilka data som är daterade eller osäkra.
