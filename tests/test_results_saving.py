import pytest
from wtf.results import save_results, save_json
import json
import datetime

def test_save_json_saving_some_data_and_metadata(tmp_path):
    results_data = {
        "1": "data",
        "2": "data",
        "3": "data",
    }
    metadata = {
        "device_name": "Maverick",
        "AP_ip": "192.168.1.1",
        "htmodes": [20,40,80,160],
        "OS": "OpenWrt",
        "Date": "1970.01.01",
    }
    path = tmp_path / "saving_some_data"
    path.mkdir()

    save_json(path, results_data, metadata)

    file_path = path / "results.json"
    metadata_path = path / "metadata.json"
    with open(file_path, "r") as file:
        data = json.load(file)
        assert data == results_data

    with open(metadata_path, "r") as file:
        data = json.load(file)
        assert data == metadata

def test_save_results_creates_results_dir_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    save_results("json", {"a":"b"}, {"metadata":"metadata"})
    results_dir = tmp_path / "results"

    assert results_dir.exists()
    assert results_dir.is_dir()

def test_save_results_rejects_unsupported_format(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError):
        save_results("noformatexist", {"a": "b"}, {"metadata": "metadata"})
    results_dir = tmp_path / "results"

    assert not results_dir.exists()
