from pathlib import Path

def test_release_readiness_assets_exist():
    root=Path(__file__).resolve().parents[1]
    assert (root/'scripts/release_readiness.py').exists()
    assert (root/'docs/release-readiness.md').exists()
    assert 'Release readiness' in (root/'.github/workflows/ci.yml').read_text(encoding='utf-8')
    assert 'Release readiness' in (root/'.github/workflows/release.yml').read_text(encoding='utf-8')

def test_release_workflow_uploads_readiness_report():
    root=Path(__file__).resolve().parents[1]
    text=(root/'.github/workflows/release.yml').read_text(encoding='utf-8')
    assert 'dist/release-readiness.json' in text
    assert 'dist/release-readiness.md' in text
