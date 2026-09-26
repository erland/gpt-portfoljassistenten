# Release readiness

`python scripts/release_readiness.py --project-root . --version <version> --check` kör den slutliga releasegrinden efter build.

Den blockerar release om lint, modellrobusthet, tester, final hygiene, distributionsvalidering, någon aktiv runtimevalidator eller runtime parity misslyckas, eller om en förväntad distributionsartefakt saknas. Rapporten skrivs till `dist/release-readiness.json` och `dist/release-readiness.md`.

GitHub CI använder `0.0.0-ci`. Release-workflow härleder versionen från release-taggen och bifogar readiness-rapporten tillsammans med ZIP-filer, checksums och delivery manifest.
