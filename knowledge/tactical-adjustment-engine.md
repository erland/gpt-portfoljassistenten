# Taktisk justeringsmotor

## Syfte

Den taktiska justeringsmotorn översätter en strukturerad investeringsstrategi till begränsade, reproducerbara avvikelser från användarens strategiska målallokering. Reglerna i detta dokument är **Portföljassistentens analysregler**. De är inte Swedbanks egna procentrekommendationer.

Motorn får aldrig använda en taktisk marknadssyn för att byta användarens långsiktiga riskprofil. Strategisk allokering är alltid utgångspunkt och riskram.

## Grundregel

1. Börja från den bekräftade strategiska allokeringen.
2. Applicera endast taktiska signaler som är aktuella och tillräckligt underbyggda.
3. Neutral signal ger delta 0.
4. En vanlig över-/undervikt motsvarar som standard **3 procentenheter**.
5. En uttryckligen tydlig/stark över-/undervikt motsvarar som standard **5 procentenheter**.
6. Justeringar måste vara finansierade: totalen ska efter varje nivå fortfarande summera till 100 procent.
7. Den taktiska aktieandelen får aldrig lämna den bekräftade riskprofilens aktieintervall eller ett striktare användarsatt intervall.
8. Inget tillgångsslag eller undersegment får bli negativt.
9. Om en signal inte kan finansieras eller appliceras inom riskramen ska den klippas till närmaste tillåtna nivå och begränsningen redovisas.
10. Om signalerna är för ofullständiga för en reproducerbar numerisk justering ska de redovisas som kvalitativa preferenser i stället för att exakta procenttal hittas på.

## Styrka

Normaliserade styrkor:

- `strong_overweight`: +5 pp
- `overweight`: +3 pp
- `neutral`: 0 pp
- `underweight`: -3 pp
- `strong_underweight`: -5 pp

`pp` betyder procentenheter på den nivå där signalen verkar.

## Tillgångsslag på portföljnivå

För huvudklasserna aktier, räntor och krediter används i första hand uttryckliga finansieringsrelationer från strategin, exempelvis "aktieövervikt finansierad av räntor".

Exempel med strategisk allokering 60/30/10 och tydlig aktieövervikt finansierad av räntor:

- aktier: 60 + 5 = 65
- räntor: 30 - 5 = 25
- krediter: 10 + 0 = 10

Om användarens riskprofil har ett aktietak på 65 blir detta exakt taket. Om taket i stället vore 63 klipps aktieökningen till +3 och ränteminskningen till -3.

### Finansieringsordning

1. Använd uttrycklig `funded_by`/motpart om sådan finns.
2. Annars använd motsatt riktade huvudsignaler som finansiering.
3. Om endast en riktning finns och ingen finansieringskälla kan härledas säkert, skapa inte en exakt portföljvikt; behåll signalen kvalitativ.

Neutral huvudkategori ska så långt möjligt behålla sin strategiska vikt. En neutral kategori får alltså inte rutinmässigt användas som finansieringskälla bara för att få matematiken att gå ihop.

## Hierarkiska signaler

Underpreferenser ändrar **sammansättningen inom sin föräldrakategori**, inte föräldrakategorins totala vikt.

### Regioner inom aktier

Regionvikter uttrycks som andelar av aktiedelen. Neutral region lämnas oförändrad. Om alla regioner är neutrala är regionfördelningen identisk med den strategiska regionbaslinjen.

När en eller flera regioner över-/underviktas:

- normal styrka flyttar 3 procentenheter av aktiesleeven,
- tydlig/stark styrka flyttar 5 procentenheter av aktiesleeven,
- explicita undervikter finansierar övervikter först,
- om en övervikt finns men ingen explicit undervikt anges får övriga neutrala regioner minskas proportionellt för att bevara 100 %, men detta ska beskrivas som matematisk finansiering och inte som en ny källhärledd undervikt,
- varje region hålls inom 0–100 % och summan normaliseras till 100 % inom aktiedelen.

## Räntor: kort kontra lång duration

Preferenser för penningmarknad/kort duration och obligationsmarknad/lång duration påverkar endast fördelningen inom räntedelen. En tydlig preferens för kort duration kan exempelvis flytta 5 procentenheter av räntesleeven från lång till kort duration. Detta ändrar inte räntornas totalvikt.

## Krediter: Investment Grade kontra High Yield

En neutral kreditvikt kan samtidigt ha en aktiv underpreferens. Övervikt High Yield på bekostnad av Investment Grade flyttar som standard 3 procentenheter inom kreditsleeven, eller 5 procentenheter om strategin uttryckligen anger en tydlig/stark preferens. Krediternas totalvikt ändras inte av denna underpreferens.

## Taktisk avvikelse och riskram

Utöver riskprofilens aktieintervall gäller följande säkerhetsramar:

- maximal automatisk förändring av total aktieandel från strategisk vikt: 5 pp per aktuell strategi,
- maximal automatisk förändring av en huvudtillgångsklass: 5 pp per aktuell strategi om inte användaren uttryckligen valt en annan taktisk ram,
- maximal automatisk förändring av ett enskilt barnsegment inom en sleeve: 5 pp av den aktuella sleeven,
- taktiska signaler får inte skapa hävstång, negativ vikt eller totalsumma över/under 100 %.

Taktiska avvikelser är temporära. Vid ny strategi ska motorn utgå från den strategiska baslinjen och den nya strategin, inte stapla nya avvikelser ovanpå föregående månads taktiska portfölj.

## Datakvalitet

Numerisk justering kräver att:

- strategin har identifierbart datum,
- signalens nivå och riktning är tydlig,
- strategin är aktuell enligt projektets evidensregler,
- strategisk baslinje och riskram är kända.

Om något av detta saknas får signalen beskrivas kvalitativt men inte omvandlas till exakt målprocent.

## September 2026 som referensfall

För den uppladdade strategin från september 2026 är de strukturerade signalerna bland annat:

- tydlig övervikt aktier, finansierad av räntor,
- tydlig undervikt räntor,
- neutral kreditvikt,
- neutral regionallokering,
- preferens för penningmarknad/kort duration framför obligationsmarknad,
- övervikt High Yield relativt Investment Grade.

För en balanserad strategisk 60/30/10-portfölj ger projektets motor därför 65/25/10 på huvudnivå, förutsatt att riskramen tillåter 65 % aktier. Regionfördelningen lämnas oförändrad. Underfördelningen inom räntor respektive krediter kan däremot justeras utan att respektive huvudvikts totalsumma ändras.

Detta 65/25/10-resultat är en konsekvens av Portföljassistentens definierade +5/-5-regel för **tydlig** över-/undervikt och ska aldrig tillskrivas Swedbank som ett publicerat exakt procentförslag.
