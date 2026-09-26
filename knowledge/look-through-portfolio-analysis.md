# Portföljassistenten – look-through-portföljanalys

## Syfte

Look-through-analysen skiljer mellan **fondvikt** och **faktisk underliggande exponering**. En globalfond, regional fond och blandfond ska därför inte behandlas som separata kategorier i slutresultatet; deras verifierade exponeringar ska viktas in i portföljen.

## Grundformel

För varje canonical kategori beräknas portföljexponeringen som:

`sum(portföljvikt_pct × fondexponering_pct / 100)`

Beräkningen görs separat för:

- tillgångsslag,
- geografiska regioner,
- valfritt land när tillräcklig källdata finns.

Kontanter som ligger direkt i portföljen adderas till `cash` i tillgångsanalysen.

## Snapshot-val

Använd senast lämpliga verifierade snapshot per fond och dimension. Exakta look-through-beräkningar ska normalt bygga på aktuell data enligt källreglerna. Om senaste snapshot är stale, conflicted eller unverified ska resultatet märkas och precisionen begränsas.

## Täckning och okänd andel

Täckning får aldrig döljas.

För en given dimension beräknas faktisk täckning från summan av rapporterade normaliserade poster, begränsad av fondens `coverage_pct`.

Exempel: en fond väger 20 % i portföljen och bara 80 % av fondens geografiska exponering kan normaliseras. Då bidrar fonden med högst 16 procentenheter känd geografisk portföljexponering och 4 procentenheter `unknown`.

Portföljresultatet ska alltid kunna redovisa:

- `known_pct`,
- `unknown_pct`,
- `coverage_pct = known_pct / total_analyzed_weight × 100`.

Saknad allokeringsdimension innebär 0 % känd täckning för den dimensionen, inte ett antagande utifrån fondnamn.

## Blandfonder och fond-i-fond

- `full`: använd normaliserade underliggande exponeringar fullt ut.
- `partial`: använd bara verifierad del och för resten till `unknown`.
- `direct`: använd direkt rapporterad allokering, men påstå inte mer granularitet än källan stöder.
- `not_available`: hela fondvikten är `unknown` för dimensionen.

Om en blandfond anger 55 % aktier, 20 % statsobligationer, 12 % IG-kredit och 5 % kassa med 92 % total täckning, ska återstående 8 % av fondvikten ligga som okänd tillgångsexponering.

## Geografi

Geografisk exponering ska normalt analyseras inom den del av portföljen där relevant geografi faktiskt kan härledas. För en ren obligationsfond utan verifierad geografisk allokering ska fonden inte automatiskt föras till Sverige eller annan region.

Två vyer kan därför vara relevanta:

1. **Helportfölj-geografi** – känd geografisk exponering som andel av hela portföljen, med explicit okänd andel.
2. **Aktiegeografi** – geografisk fördelning inom känd aktieexponering när underlaget medger koppling mellan aktiedel och regioner.

Om källan bara ger fondens övergripande geografi för en blandfond får GPT:n inte låtsas att den exakt beskriver enbart aktiedelen.

## Överlapp

Regionöverlapp mäts som flera fonders bidrag till samma canonical region. Det är inte i sig ett problem, men ska synliggöras när en portfölj har både bred global exponering och separat regional fond.

För varje region kan analysen redovisa:

- total regionexponering,
- bidrag per fond,
- största enskilda fondbidrag,
- antal innehav som bidrar materiellt.

Exempel: om en globalfond bidrar 26 procentenheter USA och en separat USA-fond bidrar 20 procentenheter USA, är den faktiska USA-exponeringen minst 46 procentenheter före övriga fonder.

## Koncentration

Portföljassistenten ska identifiera koncentration utan att hitta på universella riskgränser. Minst följande signaler får användas:

- en region står för en stor andel av den kända geografiska exponeringen,
- flera fonder duplicerar samma region eller tillgångsslag,
- en enskild fond dominerar portföljens exponering,
- okänd andel är så stor att en säker slutsats inte kan dras.

Koncentration ska beskrivas faktabaserat, till exempel `USA utgör 55 % av känd geografisk exponering`, inte automatiskt klassas som olämplig.

## Jämförelse mot målallokering

När målallokering finns beräknas avvikelse som:

`actual_pct - target_pct`

för varje jämförbar kategori. Strategisk och taktisk målbild ska hållas separata. Analysen ska kunna visa:

- avvikelse mot strategisk målallokering,
- avvikelse mot effektiv/taktiskt justerad målallokering,
- om slutsatsen påverkas av okänd täckning.

Exakta rebalanseringsförslag ska inte baseras på en dimension vars okända andel är så stor att riktningen kan ändras materiellt.

## Precision

- Intern beräkning får använda full precision.
- Svar till användaren bör normalt avrundas till 0,1 eller 1 procentenhet beroende på datakvalitet.
- Avrunda inte bort `unknown`.
- Lägg inte till eller normalisera okänd andel till 100 % kända kategorier om inte användaren uttryckligen ber om en normaliserad vy.

## Portföljanalysens minsta utdata

En look-through-analys bör minst kunna producera:

- aggregerad tillgångsfördelning,
- aggregerad geografisk fördelning,
- okänd andel och täckningsgrad per dimension,
- fondbidrag per kategori,
- identifierade överlapp,
- avvikelser mot mål när mål finns,
- datadatum och kvalitetsnoteringar.
