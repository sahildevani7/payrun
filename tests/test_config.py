import json

import pytest

from payrun.config import Config, load_config
from payrun.errors import ConfigurationError


def _mapping(**overrides):
    base = {
        "database_path": "payrun.db",
        "currency": "USD",
        "plan_year": 2026,
        "frequency": "BIWEEKLY",
    }
    base.update(overrides)
    return base


def test_from_mapping_builds_config():
    config = Config.from_mapping(_mapping())
    assert config == Config(
        database_path="payrun.db", currency="USD", plan_year=2026, frequency="BIWEEKLY"
    )


def test_from_mapping_rejects_missing_keys():
    with pytest.raises(ConfigurationError):
        Config.from_mapping({"database_path": "payrun.db"})


def test_from_mapping_rejects_malformed_plan_year():
    with pytest.raises(ConfigurationError):
        Config.from_mapping(_mapping(plan_year="not-a-year"))


def test_load_config_reads_json_file(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(_mapping(currency="CAD")))
    config = load_config(path)
    assert config.currency == "CAD"


def test_load_config_missing_file_raises(tmp_path):
    with pytest.raises(ConfigurationError):
        load_config(tmp_path / "missing.json")


def test_load_config_rejects_invalid_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{not valid json")
    with pytest.raises(ConfigurationError):
        load_config(path)


def test_load_config_rejects_non_object_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("[1, 2, 3]")
    with pytest.raises(ConfigurationError):
        load_config(path)


def test_config_is_frozen():
    config = Config(
        database_path="payrun.db", currency="USD", plan_year=2026, frequency="BIWEEKLY"
    )
    with pytest.raises(AttributeError):
        config.plan_year = 2027  # type: ignore[misc]
