import configparser
import json
import pathlib
import time
from typing import Any

import jwt
import pytest

from aicostmanager.client import CostManagerClient
from aicostmanager.config_manager import ConfigNotFound, CostManagerConfig

PRIVATE_KEY = (pathlib.Path(__file__).parent / "threshold_private_key.pem").read_text()
PUBLIC_KEY = (pathlib.Path(__file__).parent / "threshold_public_key.pem").read_text()


def _make_config_item(api_id: str = "python-client"):
    now = int(time.time())
    cfg_payload = {
        "uuid": "cfg-1",
        "config_id": api_id,
        "api_id": api_id,
        "last_updated": "2025-01-01T00:00:00Z",
        "handling_config": {"foo": "bar"},
    }
    payload = {
        "iss": "aicm-api",
        "sub": "api-key-id",
        "iat": now,
        "jti": "config",
        "version": "v1",
        "key_id": "test",
        "configs": [cfg_payload],
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256", headers={"kid": "test"})
    item = {
        "config_id": api_id,
        "api_id": api_id,
        "version": "v1",
        "public_key": PUBLIC_KEY,
        "key_id": "test",
        "encrypted_payload": token,
    }
    return item, cfg_payload


def _make_triggered_limits():
    now = int(time.time())
    event = {
        "event_id": "evt-1",
        "limit_id": "lim-1",
        "threshold_type": "limit",
        "amount": 10.0,
        "period": "day",
        "vendor": {
            "name": "openai",
            "config_ids": ["cfg1"],
            "hostname": "api.openai.com",
        },
        "service_id": "gpt-4",
        "client_customer_key": "cust1",
        "api_key_id": "api-key-id",
        "triggered_at": "2025-01-01T00:00:00Z",
        "expires_at": "2025-01-02T00:00:00Z",
    }
    payload = {
        "iss": "aicm-api",
        "sub": "api-key-id",
        "iat": now,
        "jti": "tl",
        "version": "v1",
        "key_id": "test",
        "triggered_limits": [event],
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256", headers={"kid": "test"})
    item = {
        "version": "v1",
        "public_key": PUBLIC_KEY,
        "key_id": "test",
        "encrypted_payload": token,
    }
    return item, [event]


def test_get_config_and_limits(monkeypatch, tmp_path):
    ini = tmp_path / "AICM.INI"
    client = CostManagerClient(aicm_api_key="sk-test", aicm_ini_path=str(ini))
    cfg_mgr = CostManagerConfig(client)

    config_item, cfg_payload = _make_config_item()
    tl_item, tl_events = _make_triggered_limits()

    def fake_get_configs(etag=None):
        return {"service_configs": [config_item], "triggered_limits": tl_item}

    monkeypatch.setattr(client, "get_configs", fake_get_configs)

    configs = cfg_mgr.get_config("python-client")
    assert len(configs) == 1
    assert configs[0].handling_config == cfg_payload["handling_config"]

    limits = cfg_mgr.get_triggered_limits(service_id="gpt-4")
    assert len(limits) == 1
    assert limits[0].service_id == "gpt-4"
    assert limits[0].config_id_list == ["cfg1"]
    assert limits[0].hostname == "api.openai.com"

    # file written
    cp = configparser.ConfigParser()
    cp.read(ini)
    assert cp.has_section("configs")
    assert cp.has_section("triggered_limits")


def test_config_not_found(monkeypatch, tmp_path):
    ini = tmp_path / "AICM.INI"
    client = CostManagerClient(aicm_api_key="sk-test", aicm_ini_path=str(ini))
    cfg_mgr = CostManagerConfig(client)

    config_item, _ = _make_config_item("other")
    tl_item, _ = _make_triggered_limits()
    monkeypatch.setattr(
        client,
        "get_configs",
        lambda etag=None: {
            "service_configs": [config_item],
            "triggered_limits": tl_item,
        },
    )

    with pytest.raises(ConfigNotFound):
        cfg_mgr.get_config("missing")


def test_get_triggered_limits_empty(monkeypatch, tmp_path):
    ini = tmp_path / "AICM.INI"
    client = CostManagerClient(aicm_api_key="sk-test", aicm_ini_path=str(ini))
    cfg_mgr = CostManagerConfig(client)

    config_item, _ = _make_config_item()
    now = int(time.time())
    payload = {
        "iss": "aicm-api",
        "sub": "api-key-id",
        "iat": now,
        "jti": "tl",
        "version": "v1",
        "key_id": "test",
        "triggered_limits": [],
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256", headers={"kid": "test"})
    tl_item = {
        "version": "v1",
        "public_key": PUBLIC_KEY,
        "key_id": "test",
        "encrypted_payload": token,
    }
    monkeypatch.setattr(
        client,
        "get_configs",
        lambda etag=None: {
            "service_configs": [config_item],
            "triggered_limits": tl_item,
        },
    )

    limits = cfg_mgr.get_triggered_limits()
    assert limits == []


def test_refresh_only_when_needed(monkeypatch, tmp_path):
    ini = tmp_path / "AICM.INI"
    client = CostManagerClient(aicm_api_key="sk", aicm_ini_path=str(ini))
    cfg_mgr = CostManagerConfig(client)

    called = {}

    def fake_get_configs(etag=None):
        called["count"] = called.get("count", 0) + 1
        item, _ = _make_config_item()
        tl_item, _ = _make_triggered_limits()
        return {"service_configs": [item], "triggered_limits": tl_item}

    monkeypatch.setattr(client, "get_configs", fake_get_configs)

    cfg_mgr.refresh()
    assert called["count"] == 1
    cfg_mgr.get_config("python-client")
    assert called["count"] == 1  # no additional refresh


def test_config_manager_etag(monkeypatch, tmp_path):
    ini = tmp_path / "AICM.INI"
    client = CostManagerClient(aicm_api_key="sk", aicm_ini_path=str(ini))
    cfg_mgr = CostManagerConfig(client)

    item, _ = _make_config_item()
    tl_item, _ = _make_triggered_limits()

    calls: dict[str, Any] = {"configs": [], "limits": 0}

    def fake_get_configs(etag=None):
        calls["configs"].append(etag)
        if etag == "tag1":
            client._configs_etag = "tag1"
            return None
        client._configs_etag = "tag1"
        return {"service_configs": [item], "triggered_limits": tl_item}

    tl_item2 = {"encrypted_payload": "tok2", "public_key": "pk2"}

    def fake_get_triggered_limits():
        calls["limits"] += 1
        return {"triggered_limits": tl_item2}

    monkeypatch.setattr(client, "get_configs", fake_get_configs)
    monkeypatch.setattr(client, "get_triggered_limits", fake_get_triggered_limits)

    cfg_mgr.refresh()
    assert calls["configs"] == [None]
    assert calls["limits"] == 0

    cfg_mgr.refresh()
    assert calls["configs"] == [None, "tag1"]
    # second refresh should fetch triggered limits to refresh the INI
    assert calls["limits"] == 1

    cp = configparser.ConfigParser()
    cp.read(ini)
    assert json.loads(cp["triggered_limits"]["payload"]) == tl_item2


def test_fetch_limits_when_missing(monkeypatch, tmp_path):
    """If triggered limits are absent and configs haven't changed, fetch them."""
    ini = tmp_path / "AICM.INI"
    client = CostManagerClient(aicm_api_key="sk", aicm_ini_path=str(ini))
    cfg_mgr = CostManagerConfig(client)

    tl_item, _ = _make_triggered_limits()

    calls = {"configs": 0, "limits": 0}

    def fake_get_configs(etag=None):
        calls["configs"] += 1
        client._configs_etag = "tag1"
        return None

    def fake_get_triggered_limits():
        calls["limits"] += 1
        return {"triggered_limits": tl_item}

    monkeypatch.setattr(client, "get_configs", fake_get_configs)
    monkeypatch.setattr(client, "get_triggered_limits", fake_get_triggered_limits)

    cfg_mgr.refresh()
    assert calls == {"configs": 1, "limits": 1}
    cp = configparser.ConfigParser()
    cp.read(ini)
    assert json.loads(cp["triggered_limits"]["payload"]) == tl_item


def test_triggered_limits_from_ini(monkeypatch, tmp_path):
    ini = tmp_path / "AICM.INI"
    client = CostManagerClient(aicm_api_key="sk", aicm_ini_path=str(ini))
    cfg_mgr = CostManagerConfig(client)

    item, _ = _make_config_item()
    tl_item, _ = _make_triggered_limits()

    calls = {"configs": 0, "limits": 0}

    def fake_get_configs(etag=None):
        calls["configs"] += 1
        return {"service_configs": [item], "triggered_limits": tl_item}

    def fake_get_triggered_limits():
        calls["limits"] += 1
        return {"triggered_limits": tl_item}

    monkeypatch.setattr(client, "get_configs", fake_get_configs)
    monkeypatch.setattr(client, "get_triggered_limits", fake_get_triggered_limits)

    cfg_mgr.get_config("python-client")
    assert calls == {"configs": 1, "limits": 0}
    calls["configs"] = 0
    calls["limits"] = 0

    limits = cfg_mgr.get_triggered_limits()
    assert calls == {"configs": 0, "limits": 0}
    assert len(limits) == 1
