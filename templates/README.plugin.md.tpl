# {{GPT_NAME}} — OpenAI Plugin

Version: {{VERSION}}

Detta är en genererad skills-first plugin-distribution från GPT Byggaren.

## Innehåll

Pluginpaketet innehåller:

- `plugin.json`
- en eller flera skills under `skills/`
- relevanta `references/`
- relevanta `assets/`
- runtime-relevanta `scripts/`
- `runtime-contract.json`
- `MANIFEST.json`
- `VERSION`

## Skills

{{SKILLS}}

## Installation och användning

Installera pluginpaketet enligt den aktuella ChatGPT/plugin-miljön där det ska användas.

Runtimepaketet är genererat från projektets canonical kontrakt. Runtime-specifika filer i paketet ska därför betraktas som genererade artefakter, inte som nya sanningskällor.

## Begränsningar i Plugin v1

Denna version är skills-first och genererar inte:

- MCP-servrar
- UI-komponenter
- lifecycle hooks
- marketplace-metadata

Sådana funktioner ska endast införas när projektets use case faktiskt kräver dem.

## Portabilitet

Skilldefinitioner, referenser, assets och scripts är härledda från samma canonical projektdata som övriga peer runtimes.
