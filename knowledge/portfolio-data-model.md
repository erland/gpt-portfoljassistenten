# Portföljassistenten – canonical portfölj- och fonddatamodell

## Syfte

Denna modell är provider-neutral. Swedbank är första provider i v1, men inga kärnobjekt ska förutsätta Swedbank-specifika namn, URL:er eller kategorier. Provider-specifika begrepp mappas till modellen genom `platform_availability`, källor och framtida adapters.

## Grundobjekt

### Fund

Representerar en investeringsfond oberoende av var den distribueras.

Obligatoriska kärnfält:

- `fund_id`: stabil intern identitet.
- `name`: fondens aktuella namn.
- `fund_type`: bred fondtyp, exempelvis `equity`, `fixed_income`, `mixed`, `credit` eller `fund_of_funds`.
- `currency`: fondens redovisnings-/andelsklassvaluta när den är känd.
- `identifiers`: externa identifierare, i första hand ISIN när tillgänglig.
- `platform_availability`: en eller flera uppgifter om var fonden är verifierat tillgänglig.
- `exposures`: aktuell eller senast verifierad tillgångs- och geografisk allokering.
- `risk`: riskuppgift med skala och datadatum.
- `fees`: avgiftsuppgifter med definition och datadatum.
- `performance`: historiska avkastningspunkter med period, valuta och datadatum.
- `sources`: provenance för fakta.

### PlatformAvailability

Anger var och hur fonden är verifierad som köpbar.

- `provider_id`: generiskt provider-id, exempelvis `swedbank`.
- `platform_id`: den konkreta fondplattformen eller distributionsytan.
- `account_types`: exempelvis `ISK`.
- `availability_status`: `verified`, `unverified`, `not_available` eller `unknown`.
- `verified_at`: när tillgängligheten verifierades.
- `source_id`: referens till källa.

Kärnlogiken får inte anta att `provider_id=swedbank`; andra providers ska kunna läggas till utan schemaändring.

### ExposureSnapshot

Exponering är tidsberoende och lagras därför som snapshot.

- `as_of_date`: när innehavs-/allokeringsdata gäller.
- `asset_allocation`: andelar per tillgångsslag.
- `geographic_allocation`: andelar per region/land.
- `look_through_level`: `direct`, `partial`, `full` eller `not_available`.
- `coverage_pct`: hur stor del av fonden som den normaliserade allokeringen täcker.
- `source_id`: källa för snapshoten.

#### Tillgångsslag

Canonical kategorier:

- `equity`
- `government_bonds`
- `investment_grade_credit`
- `high_yield_credit`
- `money_market`
- `cash`
- `real_estate`
- `commodities`
- `alternatives`
- `other`
- `unknown`

En källa som bara anger exempelvis "räntor 40 %" får representeras med `fixed_income_unspecified` som källkategori i `raw_label` och normaliseras till `other` eller en summerad ränteexponering med markerad osäkerhet. Modellen får inte hitta på en mer detaljerad uppdelning än källan stödjer.

#### Geografi

Canonical regioner:

- `sweden`
- `europe_ex_sweden`
- `usa`
- `canada`
- `japan`
- `developed_asia_ex_japan`
- `emerging_markets`
- `other`
- `unknown`

Landdata får lagras parallellt när källa finns. Regionerna är analyskategorier och behöver inte vara identiska med fondbolagets presentationskategorier; `raw_label` bevarar källans originalbenämning.

### Risk

Risk är inte en enda universell siffra. Modellen lagrar därför:

- `score`
- `scale_min`
- `scale_max`
- `method`, exempelvis `SRI`
- `as_of_date`
- `source_id`

Det gör att framtida providers eller äldre faktablad med annan skala kan representeras utan schemaändring.

### Fees

Varje avgiftspost ska ange vad procenten avser.

Exempel:

- `management_fee_pct`
- `ongoing_charges_pct`
- `transaction_cost_pct`
- `entry_fee_pct`
- `exit_fee_pct`

Varje post har `as_of_date` och `source_id`. Saknad avgift är `null`/utelämnad, aldrig implicit noll.

### PerformancePoint

Historisk avkastning lagras som en serie mätpunkter:

- `period`: exempelvis `YTD`, `1Y`, `3Y`, `5Y`, `10Y` eller `SINCE_INCEPTION`.
- `return_pct`
- `annualized`: om flerårsavkastningen är annualiserad eller kumulativ.
- `currency`
- `as_of_date`
- `source_id`

Historisk avkastning ska inte normaliseras mellan annualiserad och kumulativ utan att definitionen är känd.

### Portfolio

Representerar användarens portfölj eller en föreslagen portfölj.

- `portfolio_id`
- `holdings`: fondreferens och vikt i procent.
- `cash_weight_pct` vid behov.
- `profile`: risknivå, placeringshorisont och andra uttryckligen kända förutsättningar.
- `target_allocation`: strategiska och taktiska målvikter när de finns.
- `as_of_date`

Vikterna ska normalt summera till 100 %, med explicita toleranser för avrundning eller separat kontantandel.

### PortfolioHolding

- `fund_id`
- `weight_pct`
- valfritt `market_value`
- valfritt `currency`
- valfritt `user_label`

### TargetAllocation

Målallokering hålls separat från fondval:

- `strategic_asset_allocation`
- `strategic_geographic_allocation`
- `tactical_asset_allocation`
- `tactical_geographic_allocation`
- `effective_asset_allocation`
- `effective_geographic_allocation`
- `derived_at`
- `assumptions`

Det gör det möjligt att förklara vad som är långsiktig grund respektive taktisk avvikelse.

## Look-through och fond-i-fond

En blandfond eller fond-i-fond kan beskrivas på tre nivåer:

1. `direct`: bara fondens direkt rapporterade huvudallokering finns.
2. `partial`: vissa underliggande exponeringar kan genomlysas.
3. `full`: huvudsaklig underliggande exponering kan fördelas på canonical tillgångsslag/regioner.

När genomlysningen inte täcker 100 % ska `coverage_pct` anges och återstoden behandlas som `unknown`/`other` i portföljanalysen. GPT:n får inte fylla luckan med antaganden utan att märka dem som antaganden.

## Provenance och aktualitet

Alla föränderliga datapunkter ska kunna härledas till en källa genom `source_id`. En källa bör minst innehålla:

- `source_id`
- `publisher`
- `title`
- `url` eller filreferens när relevant
- `published_at` om känt
- `retrieved_at`
- `source_type`, exempelvis `platform`, `fund_company`, `factsheet`, `monthly_report`, `third_party`

`as_of_date` beskriver när datapunkten gäller; `retrieved_at` beskriver när källan hämtades. Dessa får inte blandas ihop.

## Beräknad portföljexponering

För varje canonical kategori beräknas portföljens exponering som:

`sum(holding_weight_pct × fund_exposure_pct / 100)`

Beräkningen ska samtidigt hålla reda på täckningsgrad. Om en fond saknar fullständig exponering ska resultatet inte presenteras med falsk precision.

## Providerneutralitet

Följande är uttryckligen förbjudet i kärnschemat:

- Swedbank-specifika fältnamn.
- antagandet att endast ISK finns som kontotyp.
- antagandet att Swedbanks regionsindelning är universell.
- koppling mellan fondidentitet och en viss banks interna produkt-id.

Provider-specifika värden får finnas som data, inte som schemastruktur.
