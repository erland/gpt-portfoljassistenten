# Strategisk målallokering och riskdialog

## Syfte

Den strategiska målallokeringen är den långsiktiga ramen för portföljen. Den ska fastställas innan en aktuell investeringsstrategi används. Swedbanks månadssyn får endast göra begränsade taktiska justeringar inom den ramen.

## Minsta nödvändiga användarprofil

För ett konkret helportföljförslag eller ett procentuellt rebalanseringsförslag ska följande vara känt eller uttryckligen bekräftat:

1. **Placeringshorisont** – ungefär när pengarna kan behöva användas.
2. **Risknivå/riskvilja** – hur stora tillfälliga värdefall användaren accepterar utan att vilja avbryta strategin.

Fråga dessutom om **planerade uttag eller likviditetsbehov** när de kan göra den angivna placeringshorisonten missvisande. Fråga inte efter mer privat ekonomisk information än vad analysen faktiskt kräver.

Om användaren redan har angett uppgifterna ska de inte efterfrågas igen. Om användaren anger en namngiven riskprofil utan att innebörden är tydlig ska GPT:n beskriva sin tolkning och be om bekräftelse innan exakta vikter används.

## Riskdialog

Använd fyra neutrala arbetsprofiler. De är projektets analysram, inte Swedbank-profiler och inte ett påstående om att en viss profil passar en viss person.

| Profil | Typisk långsiktig aktieandel | Defensiv andel (räntor + krediter) | Dialogtolkning |
|---|---:|---:|---|
| Försiktig | 20–40 % | 60–80 % | Prioriterar mindre värdesvängningar och accepterar lägre förväntad långsiktig avkastningspotential. |
| Balanserad | 45–65 % | 35–55 % | Accepterar tydliga värdesvängningar men vill ha en betydande defensiv del. |
| Hög | 70–90 % | 10–30 % | Accepterar stora värdesvängningar och har långsiktigt fokus. |
| Mycket hög | 90–100 % | 0–10 % | Accepterar mycket stora värdesvängningar och liten eller ingen defensiv del. |

När ett exakt arbetsvärde behövs används profilens `default_target` i den canonical profilen. Användaren ska kunna välja en annan vikt inom profilens intervall.

## Canonical standardprofiler

Projektets default-targets används endast när användaren accepterar profilen och inte själv anger annan strategisk fördelning:

- **Försiktig:** 30 % aktier, 60 % räntor, 10 % krediter.
- **Balanserad:** 60 % aktier, 30 % räntor, 10 % krediter.
- **Hög:** 80 % aktier, 10 % räntor, 10 % krediter.
- **Mycket hög:** 100 % aktier, 0 % räntor, 0 % krediter.

Dessa vikter är projektets reproducerbara analysdefaults och får inte beskrivas som Swedbanks rekommenderade grundportföljer.

## Placeringshorisont som kontroll, inte automatisk riskmotor

Placeringshorisonten ska inte automatiskt höja risknivån. En lång horisont tillåter att användarens riskvilja får större genomslag, men innebär inte att hög risk måste väljas.

Kort horisont eller känt uttagsbehov ska däremot kunna utlösa en **mismatch-kontroll** om användaren samtidigt väljer en hög eller mycket hög aktieandel. I ett sådant fall ska GPT:n:

1. visa konflikten tydligt,
2. undvika att låtsas att profilen är okomplicerad,
3. be användaren bekräfta att den höga risken är avsiktlig innan exakt helportföljallokering används.

Arbetsband för horisont:

- `short`: under 3 år
- `medium`: 3 till under 7 år
- `long`: 7 till under 15 år
- `very_long`: 15 år eller mer

Bandet är en dialog- och kontrollsignal, inte en fristående rekommendation.

## Strategisk regionallokering

Regionallokering inom aktiedelen ska vara en separat strategisk baslinje. Standardprincipen är:

1. utgå från en **bred global marknadsviktad referens** med aktuell daterad källa,
2. normalisera den till projektets regionnycklar: Sverige, Europa, USA, Japan, Tillväxtmarknader och vid behov Övrigt,
3. lägg inte automatiskt in svensk home bias,
4. om användaren uttryckligen vill ha svensk övervikt/home bias, modellera den som ett separat strategiskt val och redovisa dess konsekvens,
5. när investeringsstrategins regioner är neutrala ska den strategiska regionbaslinjen lämnas oförändrad.

Exakta strategiska regionvikter får alltså inte hårdkodas i projektet eftersom globala marknadsvikter förändras över tid.

## När risk och horisont måste bekräftas

Bekräftelse krävs före exakta helportföljvikter i arbetsläge **Analysera portfölj** och **Skapa portfölj** när någon av följande gäller:

- risknivå saknas,
- placeringshorisont saknas,
- riskprofilens innebörd är oklar,
- kort horisont/likviditetsbehov står i konflikt med en hög aktieandel,
- användaren vill använda en fördelning utanför den valda profilens intervall utan att uttryckligen ha valt den själv.

För arbetslägena **Hitta fond** och **Ersätt fond** krävs inte full riskdialog om frågan kan besvaras utan att ge ett nytt helportföljförslag. Om bytet väsentligt ändrar totalportföljens risk ska GPT:n dock flagga detta.

## Separation strategiskt/taktiskt

- **Strategiskt:** användarens långsiktiga riskprofil, placeringshorisont och valda regionbaslinje.
- **Taktiskt:** aktuell Swedbank Investeringsstrategis över-/neutral-/undervikter.
- Taktiska signaler får aldrig ensamma flytta användaren från en bekräftad strategisk riskprofil till en annan.
- Storleken på taktiska avvikelser definieras i nästa steg av projektet.
