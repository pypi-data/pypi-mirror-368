import csv
import json

import pandas as pd
import pytest

from src.berroutils.container.list_of_dict_container import ListOfDictContainer, KeyCheck
from src.berroutils.plugins.file_handler import FileHandler, JsonFileHandler


class EnergyContainer(ListOfDictContainer):
    required_keys = {'date', 'gas', 'water', 'electricity'}
    alternative_keys = {"wasser": "water",
                        "strom" : "electricity", "datum": "date"}

    def __init__(self, filehandler: FileHandler):
        super().__init__(filehandler)

    def __str__(self):
        return "EnergyContainer"


@pytest.fixture
def container(fp_ldc_energy):
    json_handler = JsonFileHandler(file_path=fp_ldc_energy)
    return EnergyContainer(filehandler=json_handler)


def test_init(container):
    assert len(container) == 7
    assert container.data[0] == {
        "date"       : 1727136000000,
        "gas"        : 196.416,
        "water"      : 530.366,
        "electricity": 269.0,
        "comment"    : "Heizungswartung 2024"
    }


# @pytest.mark.skip("wip")
def test_add(container, tmp_path):
    other_data = [{
        "date"       : 1740700800000,
        "gas"        : 1904.9,
        "water"      : 625.631,
        "electricity": 2135.0,
        "comment"    : "Jahresablesung Strom"
    }]
    other_path = tmp_path / "other_test.json"
    json_handler = JsonFileHandler(file_path=other_path)
    other_container = EnergyContainer(filehandler=json_handler)
    other_container.update_from_upload(data=other_data)

    container.add(other_container)

    assert len(container) == 8
    assert container.find(search={"date": 1740700800000}) == other_data


@pytest.mark.parametrize("data, expected_result", [
    ([{
        "date"       : 1727136000000,
        "gas"        : 196.416,
        "water"      : 530.366,
        "electricity": 269.0,
        "comment"    : "Heizungswartung 2024"
    }], KeyCheck(valid=True, missing_keys=set())),
    ([{
        "datum" : 1740700800000,
        "gas"   : 1904.9,
        "wasser": 625.631,
        "strom" : 2135.0
    }], KeyCheck(valid=True, missing_keys=set())),
    ([{
        "wrong_key": 1740700800000,
        "gas"      : 1904.9,
        "strom"    : 2135.0
    }], KeyCheck(valid=False, missing_keys={"date", "water"}))])
def test_contains_required_keys(container, data, expected_result):
    key_check = container.contains_required_keys(data)
    assert key_check == expected_result


def test_update_from_file_json(container, tmp_path):
    new_data = [{
        "date"       : 1,
        "gas"        : 2,
        "water"      : 3,
        "electricity": 4}]
    new_path = tmp_path / "update_test.json"
    with open(new_path, "w") as f:
        json.dump(new_data, f)
    container.update_from_file(new_path)
    assert container.data == new_data


def test_update_from_file_csv(container, tmp_path):
    new_data = [{
        "date"       : 5,
        "gas"        : 6,
        "water"      : 7,
        "electricity": 8}]
    new_path = tmp_path / "update_test.csv"

    with open(new_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=new_data[0].keys())
        writer.writeheader()
        for row in new_data:
            writer.writerow(row)

    container.update_from_file(new_path)
    assert container.data == new_data


def test_update_from_file_xlsx(container, tmp_path):
    new_data = [{
        "date"       : 1,
        "gas"        : 2,
        "water"      : 3,
        "electricity": 4}]
    new_path = tmp_path / "update_test.xlsx"
    df = pd.DataFrame(new_data)
    df.to_excel(new_path)
    container.update_from_file(new_path)
    assert container.data == new_data


def test_get_entries(container):
    entries = container.get_entries("date", 1727136000000)
    assert entries == [{
        "date"       : 1727136000000,
        "gas"        : 196.416,
        "water"      : 530.366,
        "electricity": 269.0,
        "comment"    : "Heizungswartung 2024"
    }]


def test_find(container):
    search = {"date": 1727136000000}
    display = {"gas": 1}
    results = container.find(search, display)
    assert results == [{"gas": 196.416}]


def test_last_update(container):
    assert isinstance(container.last_update, str)
