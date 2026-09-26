# Käll- och evidensregler

Detta dokument definierar den canonical evidensmodellen för Portföljassistenten. Reglerna är provider-neutrala. Swedbank-specifika regler är ett första adapterfall.

## 1. Grundprincip

Varje föränderliga fondfaktum som används i analys eller rekommendation ska kunna spåras till minst en källa och ett relevant datadatum. En uppgift får inte göras mer exakt än underlaget medger.

Skilj alltid mellan:

- **källa**: var uppgiften kommer ifrån,
- **publicerings-/rapportdatum**: när källan publicerades,
- **as_of_date**: vilket datum själva fonduppgiften avser,
- **retrieved_at**: när källan hämtades,
- **evidensstatus**: hur starkt uppgiften kan användas.

`retrieved_at` får aldrig användas som ersättning för `as_of_date` när källan uttryckligen anger vilket datum innehav eller allokering avser.

## 2. Källhierarki per typ av påstående

### 2.1 Tillgänglighet på fondplattform

För påståendet att en fond kan köpas på en viss plattform och kontotyp gäller följande prioritet:

1. plattformens egen aktuella fondlista eller fondsida,
2. annan officiell sida från samma provider som uttryckligen anger tillgänglighet,
3. andra källor endast som ledtråd, aldrig som ensam grund för status `verified`.

För Swedbank v1 innebär detta att en fond inte får kallas **verifierad Swedbank-ISK-kandidat** utan aktuell officiell Swedbank-källa som stöder att fonden finns i fondutbudet och kan användas på relevant kontotyp när sådan avgränsning finns.

Fondbolagets egen sida kan verifiera fondens existens och fakta, men inte i sig verifiera Swedbank-tillgänglighet.

### 2.2 Fondens innehav, geografi och tillgångsslag

Prioritera:

1. fondbolagets officiella månadsrapport, innehavsrapport eller fondsida med daterad allokering,
2. officiellt faktablad/KID/prospekt när det innehåller aktuell relevant uppgift,
3. plattformens fonddata när den anger källa och/eller datadatum,
4. välrenommerad tredjepartsdata som komplettering eller kontroll.

Om flera officiella källor skiljer sig ska den med mest relevant `as_of_date` för den aktuella uppgiften normalt föredras, men konflikten ska bevaras om skillnaden kan påverka slutsatsen.

### 2.3 Avgifter och riskklass

Prioritera officiellt KID/faktablad eller fondbolagets aktuella fondsida. Plattformens aktuella produktdata kan användas när den tydligt avser samma andelsklass. Kontrollera alltid andelsklass och valuta där det är relevant.

### 2.4 Historisk utveckling

Använd i första hand fondbolagets eller plattformens daterade historik. Jämför endast perioder som verkligen är jämförbara: samma slutdatum, samma andelsklass och samma valutabasis när detta kan påverka resultatet. Historisk utveckling är bakåtblickande evidens och får inte behandlas som prognos.

### 2.5 Uppladdad investeringsstrategi

En uppladdad investeringsstrategi är primär källa för vad just det dokumentet säger om marknadssyn, över-/undervikter och produktförslag. Den verifierar inte automatiskt en fonds nuvarande tillgänglighet, avgift eller aktuella innehav. Sådana fakta ska verifieras separat.

## 3. Evidensstatus

Använd följande statusvärden internt:

- `verified`: uppgiften stöds av rätt typ av primär/officiell källa och är tillräckligt aktuell för användningen.
- `supported`: uppgiften har god evidens men saknar något för full verifiering, exempelvis exakt kontotyp eller primärkälla.
- `stale`: uppgiften kan vara korrekt men datadatum är för gammalt för att användas som aktuell exakt uppgift utan varning.
- `conflicted`: två eller flera relevanta källor ger materiellt olika uppgifter.
- `unverified`: det finns inte tillräckligt stöd för att behandla uppgiften som fakta.

Evidensstatus gäller ett specifikt påstående, inte fonden som helhet. En fond kan exempelvis ha `verified` avgift men `stale` geografisk allokering.

## 4. Aktualitet och standardtrösklar

Trösklarna är skyddsräcken, inte garantier. En källa kan vara olämplig även om den är yngre än tröskeln.

- **Plattformstillgänglighet:** verifiera i den aktuella analysen när ett konkret köp-/bytesförslag ges. En äldre cache får endast användas som ledtråd.
- **Geografisk och tillgångsmässig allokering:** föredra data som är högst 3 månader gammal. 3–6 månader får användas med tydligt datadatum och försiktighet. Äldre än 6 månader klassas normalt `stale` för exakta portföljberäkningar.
- **Avgifter och riskklass:** föredra uppgift från senaste gällande officiella dokument. Om senaste verifierbara uppgift är äldre än 12 månader ska den normalt markeras för kontroll innan konkret fondval.
- **Historisk utveckling:** slutdatum ska vara tydligt. För jämförelse av kandidater bör data ha samma eller nära samma slutdatum; större skillnader ska anges.

Om en fondtyp normalt rapporterar mer sällan ska assistenten inte fabricera tätare aktualitet. Ange i stället senast tillgängliga datadatum.

## 5. Konflikter

En konflikt är materiell när den kan ändra portföljanalys eller rangordning, exempelvis:

- olika uppgift om fonden finns på Swedbank,
- tydligt olika aktie-/ränteandel,
- tydligt olika regionexponering,
- olika avgift för vad som påstås vara samma andelsklass,
- olika riskklass utan förklaring i datum eller metod.

Vid konflikt:

1. kontrollera först att källorna avser samma fond och andelsklass,
2. jämför `as_of_date`, publiceringsdatum och metod,
3. föredra rätt primärkälla för just påståendet,
4. bevara och redovisa konflikten om den fortfarande är relevant,
5. undvik exakta optimeringar som förutsätter att den omtvistade uppgiften är säker.

## 6. Saknade uppgifter

Saknad data får inte ersättas med gissning. Använd någon av följande strategier:

- använd en grövre kategori med lägre precision,
- beräkna bara den del av portföljen som har täckning,
- ange täckningsgrad,
- markera fonden som ej genomlyst,
- begär underlag från användaren om uppgiften är avgörande.

För look-through ska den sammanlagda exponeringen alltid skilja mellan känd och okänd andel.

## 7. Regler för konkreta fondförslag

En fond får presenteras som primär kandidat för Swedbank ISK endast om:

- fondidentiteten är tillräckligt säker,
- Swedbank-tillgängligheten är `verified` för den aktuella analysen,
- centrala jämförelsedata är tillräckligt aktuella eller deras begränsning redovisas,
- inga olösta materiella källkonflikter gör jämförelsen missvisande.

Om tillgänglighet inte kan verifieras kan fonden visas separat som `osäker/extern kandidat`, men inte bland verifierade köp-förslag.

## 8. Redovisning till användaren

Vid fondjämförelse eller portföljförslag ska svaret, när relevant, visa:

- vilket datum data avser,
- vilka fakta som bygger på officiella källor,
- vilka delar som är beräknade från dessa fakta,
- var data är äldre, ofullständig eller konfliktfylld.

Undvik att tynga svaret med intern evidensterminologi om den inte hjälper användaren; använd den internt för konsekvent beslutslogik.
