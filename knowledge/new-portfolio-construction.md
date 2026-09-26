# Scenario B – skapa ny portfölj

## Syfte

Detta flöde skapar ett nytt fondportföljförslag från bekräftad riskprofil, placeringshorisont, strategisk målallokering och eventuell taktisk investeringsstrategi. V1 begränsar konkreta huvudförslag till fonder som kan verifieras som tillgängliga för privatkund via Swedbank ISK.

Målet är inte att maximera historisk avkastning utan att översätta en definierad målallokering till ett litet antal verifierade byggblock och därefter kontrollera portföljens faktiska look-through-exponering.

## 1. Obligatoriska gates

Exakta fondvikter för en ny helportfölj kräver:

- bekräftad riskprofil eller uttryckligt accepterat aktieintervall,
- bekräftad placeringshorisont,
- hanterade varningsflaggor för kort horisont/närtida uttag,
- strategisk målallokering som summerar till 100 %, och
- tillräckligt verifierade fondkandidater för de byggblock som behövs.

Om risk/horizont saknas ska status vara `needs_profile_confirmation` och GPT:n ska inte ange exakta helportföljvikter.

## 2. Från strategisk till effektiv målbild

Arbeta i följande ordning:

1. skapa strategisk tillgångsallokering,
2. skapa strategisk regionbaslinje inom aktiedelen från aktuell global marknadsviktad referens,
3. applicera eventuell taktisk strategi inom riskramen,
4. härled effektiv top-level-allokering för `equity`, `rates` och `credit`,
5. härled child-sleeves inom aktier, räntor och krediter.

Regionvikter anges **inom aktiedelen**. Ränte- och kreditsegment anges inom respektive sleeve. En neutral taktisk signal lämnar den strategiska child-fördelningen oförändrad.

## 3. Byggblock och fondroller

Första versionen föredrar transparenta byggblock när de finns:

- aktiefond med tydlig regionroll,
- kort eller lång räntefond för räntesleeven,
- Investment Grade eller High Yield för kreditsleeven.

En fond får användas som exakt byggblock bara när aktuell look-through-data stödjer rollen tillräckligt tydligt. Som referensregel krävs normalt minst 95 % känd relevant exponering och minst 90 % koncentration mot avsedd child-roll för ett rent byggblock.

Blandfonder kan användas senare eller när användaren uttryckligen föredrar dem, men de får inte göra konstruktionen ogenomskinlig. Om en blandfond används måste portföljens faktiska exponering räknas om efter fondvalet.

## 4. Verifierad Swedbank-ISK-tillgänglighet

En fond får ingå som verifierat huvudförslag endast om det finns aktuell officiell Swedbank-evidens för att rätt fond/andelsklass kan köpas på ISK.

Om en nödvändig kategori saknar verifierad kandidat:

- skapa inte en låtsasfond,
- fyll inte automatiskt luckan med en extern fond,
- markera kategorin som `unresolved`,
- redovisa målvikten för den olösta kategorin,
- ge eventuella osäkra kandidater separat och märk dem `unverified`.

Portföljstatus ska då vara `insufficient_verified_candidates`, inte `complete`.

## 5. Fondurval inom en roll

När flera verifierade kandidater fyller samma roll ska urvalet vara reproducerbart och inte baseras på historisk vinnare. Följande ordning används som standard i scenario B:

1. matchning mot avsedd exponering,
2. datatäckning och aktualitet,
3. löpande avgift när jämförbar data finns,
4. risk och förvaltningsstil som rimlighetskontroll,
5. deterministisk tie-break på fond-id.

Historisk utveckling får användas som bakgrund och jämförelse men inte som ensam urvalsregel.

## 6. Översättning till fondvikter

När rena byggblock används beräknas fondvikter hierarkiskt:

- aktieregion: `equity_weight × region_weight_within_equity`,
- räntesegment: `rates_weight × segment_weight_within_rates`,
- kreditsegment: `credit_weight × segment_weight_within_credit`.

Exempel: 60 % aktier och 50 % USA inom aktiedelen ger 30 % portföljvikt i USA-byggblocket.

Fondvikterna måste summera till 100 % inom avrundningstolerans. Om en kategori är olöst ska den olösta målvikten hållas explicit och summan av valda fonder plus olösta slots vara 100 %.

## 7. Kontroll av faktisk exponering

Efter fondvalet ska GPT:n alltid räkna om:

- faktisk top-level tillgångsexponering,
- faktisk regionfördelning inom aktiedelen,
- känd/okänd andel,
- avvikelse från effektiv målbild.

Det räcker inte att fondvikterna matematiskt motsvarar målvikterna. Om look-through visar materiell avvikelse ska konstruktionen justeras eller reservation redovisas.

### Datakvalitetsgate

För en komplett ny portfölj bör relevant okänd look-through-andel normalt vara högst 2 procentenheter. Mellan 2 och 5 procentenheter krävs tydlig reservation. Över 5 procentenheter ska status normalt inte vara `complete`.

Detta är Portföljassistentens försiktighetsregel, inte en regel från Swedbank.

## 8. Svarskontrakt

Ett komplett förslag ska minst redovisa:

1. riskprofil och placeringshorisont,
2. strategisk respektive effektiv/taktisk målallokering,
3. föreslagna fonder och portföljvikter,
4. verifieringsstatus för Swedbank ISK,
5. faktisk beräknad exponering efter look-through,
6. centrala avgifter/riskdata som använts i urvalet,
7. källor och datadatum,
8. antaganden, osäkerheter och eventuella olösta slots.

Skilj alltid mellan bankens publicerade marknadssyn och Portföljassistentens egen översättning till portföljvikter.
