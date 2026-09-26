from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_required_project_files_exist():
    for rel in [
        "README.md", "PROJECT.md", "STATUS.md", "gpt-project.yaml",
        "project-status.yaml", "docs/development-plan.md", "assistant/instructions.md"
    ]:
        assert (ROOT / rel).is_file(), rel


def test_sweden_provider_is_not_core_schema_name():
    cfg = yaml.safe_load((ROOT / "gpt-project.yaml").read_text(encoding="utf-8"))
    assert cfg["project"]["id"] == "portfoljassistenten"
    assert cfg["model_robustness"]["level"] == "guided"
    assert cfg["runtime"]["chat_zip"]["enabled"] is True
    assert cfg["runtime"]["custom_gpt"]["enabled"] is True
    assert cfg["runtime"]["claude"]["enabled"] is True
