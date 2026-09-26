# Källkvalitet och evidens

## Källhierarki

- Uppladdad investeringsstrategi är primär källa för vad just det dokumentet säger om taktisk marknadssyn och produktförslag.
- Officiell Swedbank-källa krävs för status `verified` när påståendet gäller att en fond kan köpas via Swedbank ISK.
- Fondbolagets officiella månadsrapport/fondsida/faktablad prioriteras för fondens innehav, geografi, tillgångsslag, avgifter och risk, beroende på vilken källa som faktiskt innehåller uppgiften.
- Tredjepartsdata får komplettera, kontrollera och hjälpa till att hitta källor, men ska normalt inte ensam övertrumfa en relevant aktuell primärkälla.

## Datadatum

Skilj mellan publiceringsdatum, `as_of_date` och hämtningstid. För föränderliga fondfakta ska `as_of_date` anges när det finns. Använd inte hämtningstid som ersättning för fondens verkliga rapportdatum.

Standard för aktualitet:

- Swedbank-tillgänglighet: verifiera i den aktuella analysen för konkreta köp-/bytesförslag.
- Geografi/tillgångsslag: föredra <= 3 månader; 3–6 månader kräver försiktighet; > 6 månader är normalt `stale` för exakt look-through.
- Avgift/risk: använd senaste gällande officiella uppgift; > 12 månader bör kontrolleras före konkret fondval.
- Historik: redovisa slutdatum och jämför likvärdiga perioder/andelsklasser.

## Evidensstatus

Använd internt: `verified`, `supported`, `stale`, `conflicted`, `unverified`.

Status gäller ett specifikt påstående. En fond kan alltså ha verifierad avgift men stale regionallokering.

## Konflikter

Vid motstridiga uppgifter:

1. kontrollera fond och andelsklass,
2. jämför datadatum och metod,
3. använd rätt primärkälla för påståendet,
4. redovisa kvarstående materiell konflikt,
5. undvik överdriven precision tills konflikten är löst.

## Saknad data

Gissa inte. Ange täckningsgrad eller okänd andel och begränsa slutsatsen. För look-through ska känd och okänd exponering hållas isär.

## Gate för Swedbank ISK

En fond får inte presenteras som verifierad primär Swedbank-ISK-kandidat utan aktuell officiell Swedbank-evidens för tillgänglighet. Fondbolagets egen sida verifierar fondfakta men inte i sig Swedbank-tillgänglighet.
