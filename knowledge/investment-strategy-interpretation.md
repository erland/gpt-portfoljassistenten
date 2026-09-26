# Tolkning av Swedbanks Investeringsstrategi

## Syfte

Den uppladdade investeringsstrategin ska normaliseras till en reproducerbar modell av taktiska signaler. Modellen ska beskriva **vad Swedbank över-/neutral-/underviktar**, utan att blanda ihop det med användarens långsiktiga riskprofil eller med de enskilda produktförslag som banken listar.

## Tolkningsordning

1. Identifiera dokumenttitel och strategidatum från framsida eller motsvarande metadata.
2. Läs sammanfattning/allokeringsöversikt för signaler på högsta nivå.
3. Bekräfta varje signal i relevant detaljavsnitt när sådant finns.
4. Strukturera signalerna hierarkiskt:
   - tillgångsslag: aktier, räntor, krediter,
   - aktieregioner: Sverige, Europa, USA, Japan, Tillväxtmarknader,
   - räntesegment: penningmarknad/kort duration och obligationsmarknad/lång duration,
   - kreditsegment: Investment Grade och High Yield,
   - eventuella explicita regionala preferenser inom kredit.
5. Extrahera produktförslag till ett **separat** fält. Produktförslag får aldrig i sig skapa eller förstärka en allokeringssignal.
6. Extrahera affärsförslag separat som satellit-/spetsidéer. De ska inte räknas som strategiska normalvikter.

## Normalisering av viktbegrepp

- `övervikt` → `overweight`
- `tydlig övervikt` → `overweight` med `strength=clear`
- `neutralvikt`/`neutral vikt` → `neutral`
- `undervikt` → `underweight`
- `tydlig undervikt` → `underweight` med `strength=clear`
- uttryck som `föredrar X framför Y` → `X=prefer`, `Y` får motsvarande relativ negativ preferens endast om texten uttryckligen stödjer det
- uttryck som `undviker obligationsfonder` → `avoid` för obligationsmarknad/lång duration

En signal är relativ, inte en absolut procentsats. Modellen får **inte** själv översätta en övervikt till exempelvis +5 procentenheter; det görs först i den taktiska justeringsmotorn.

## Neutralvikt

Neutralvikt betyder samma vikt som den definierade strategiska normalvikten eller relevanta kategoribaslinjen. Den får aldrig tolkas som lika vikt mellan regioner eller underkategorier.

Exempel: om Sverige, Europa, USA, Japan och Tillväxtmarknader alla är neutralviktade betyder det att regionmixen ska lämnas vid den strategiska normalfördelningen, inte 20 procent vardera.

## Högsta nivå kontra undernivå

En neutral signal på överordnad nivå kan samexistera med aktiva signaler under den nivån.

Exempel:
- krediter totalt: `neutral`
- High Yield inom krediter: `overweight`
- Investment Grade inom krediter: motsvarande finansierande undervikt när dokumentet uttryckligen säger att HY överviktas på bekostnad av IG.

Likadant kan räntor totalt vara underviktade samtidigt som penningmarknaden föredras framför obligationsmarknaden inom den kvarvarande räntedelen.

## Produktförslag

Produktförslag är kandidater som banken kopplar till sin marknadssyn. De ska lagras separat med kategori och källsida. De är inte automatiskt bästa val för användaren. Vid konkret fondval måste de fortfarande verifieras mot Swedbanks aktuella ISK-utbud och jämföras enligt fondurvalsreglerna.

## Affärsförslag

Affärsförslag är enligt strategin tänkta att komplettera eller i begränsad utsträckning ersätta befintliga innehav och skapa en spets i portföljen. De får därför inte användas som kärnallokering utan uttrycklig användaravsikt och efter separat riskbedömning.

## Referensfall: september 2026

Dokumentet *Guldkantad tillvaro – Investeringsstrategin September 2026* ger följande normaliserade huvudsignaler:

- Aktier: tydlig övervikt.
- Räntor: tydlig undervikt.
- Krediter: neutral vikt.
- Sverige: neutral.
- Europa: neutral.
- USA: neutral.
- Japan: neutral.
- Tillväxtmarknader: neutral.
- Penningmarknad/kort duration: föredras inom räntor.
- Obligationsmarknad/lång duration: undviks/underprioriteras inom räntor.
- High Yield: övervikt inom krediter.
- Investment Grade: underprioriteras relativt High Yield; strategin säger uttryckligen att HY-övervikten sker på bekostnad av IG.

Strategin listar också produktförslag för varje region och ränte-/kreditsegment samt separata affärsförslag. Dessa hålls åtskilda från signalmodellen.

## Fel- och osäkerhetshantering

- Om sammanfattning och detaljavsnitt motsäger varandra: markera `conflicted` och redovisa båda.
- Om en region saknar uttrycklig rekommendation: använd `unknown`, inte `neutral`.
- Om dokumentdatum saknas: be användaren bekräfta aktualiteten innan strategin används taktiskt.
- Om strategin är gammal jämfört med den avsedda taktiska horisonten: markera strategin som daterad och använd den inte som aktuell marknadssignal utan uttryckligt godkännande.
- Inferera inte procentsatser från grafiska staplar om exakta siffror inte framgår tillförlitligt.
