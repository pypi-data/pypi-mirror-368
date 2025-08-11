import json
import logging
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

import pandas as pd
from berroutils.plugins.file_handler import FileHandler

KeyCheck = namedtuple("KeyCheck", "valid missing_keys")


class ListOfDictContainer(metaclass=ABCMeta):
    required_keys: set[str] = None
    alternative_keys: dict[str] = None

    # format: alternative_keys = {"alt_key": "unique_key"}

    @abstractmethod
    def __str__(self):
        pass

    def __init__(self, filehandler: FileHandler):
        """initiate from json file"""
        self.filehandler = filehandler
        self.data = filehandler.load() or []

    def __iter__(self):
        """make the content of the class iterable"""
        return iter(self.data)

    def __len__(self):
        """return the number of entries"""
        return len(self.data)

    def add(self, other):
        """outer join with another instance of this class

        This instance will be updated with the content of the other instance"""
        if type(other) is not type(self):
            error_message = f"other is type {type(other)}, expected type {type(self)}"
            logging.warning(error_message)
            raise ValueError(error_message)
        self.data += other.data
        self.filehandler.save(data=self.data)
        return self.data

    def _clean_data(self, data):
        return data

    def _unique_keys(self, data) -> List[dict]:
        """change keys in data to predefined keys

        `alternative_keys` defines known alternative keys and maps them to the predefined keys
        All other keys will be maintained.

        Returns: data
        """
        if self.alternative_keys:
            unique = []
            for elem in data:
                unique_elem = {self.alternative_keys.get(k, k.strip("'")): v for k, v in elem.items()}
                unique.append(unique_elem)
            return unique
        else:
            return data

    def contains_required_keys(self, dataset: list[dict]) -> KeyCheck:
        """check if given dataset contains all required keys.

        Alternative keys will be recognized and converted to the corresponding required keys

        Args:
            dataset: The dataset to be checked

        Returns:
            (bool, list of missing keys)
        """
        if not self.required_keys:
            raise ValueError("required_keys are not defined")
        given_unique_keys = set(self._unique_keys(dataset[:1])[0].keys())
        valid = True if self.required_keys.issubset(given_unique_keys) else False
        missing_keys = self.required_keys - given_unique_keys

        return KeyCheck(valid, missing_keys)

    def save(self) -> None:
        self.filehandler.save(data=self.data)

    def update_from_file(self, filepath: Path) -> None:
        """update both the storage file and instance of the class from a file.
        Implemented file-types: json, csv, xlsx"""
        match filepath.suffix:
            case '.json':
                with open(filepath) as f:
                    raw_data = json.load(f)
                self.update_from_upload(data=raw_data)

            case '.csv':
                df = pd.read_csv(filepath,
                                 header=0,  # use the first row as column names
                                 encoding='utf-8')
                raw_data = df.to_dict(orient='records')
                self.update_from_upload(data=raw_data)

            case '.xlsx' | '.xls':
                df = pd.read_excel(filepath)
                raw_data = df.to_dict(orient='records')
                self.update_from_upload(data=raw_data)

            case _:
                raise NotImplementedError

    def update_from_upload(self, data: list[dict]) -> None:
        """update both the json file and instance of the classe from a dataset."""
        unique_data = self._unique_keys(data=data)
        self.data = self._clean_data(unique_data)
        self.filehandler.save(data=self.data)

    def get_entries(self, key, value, data: list[dict] = None) -> list:
        """get all entries with a given key value pair"""
        results = []
        data_to_search = data or self.data
        for entry in data_to_search:
            if str(entry.get(key)) == str(value):
                results.append(entry)
        return results

    def get_entries_partial(self, key, expression):
        """get all entries with the expression being part of the key's value"""
        results = []
        for entry in self.data:
            if expression in entry.get(key):
                results.append(entry)
        return results

    def find(self, search: dict, display: dict = None) -> List[dict]:
        """retrieve dictionary in a list of dicts that contains given key value pair(s).

        A mongo-like search function that searches data (a list of dictionaries),
        returns a list with all elements in data that fulfill the key value pairs in the search dictionary
        and if the optional display dictionary is specified, return keys with value 1 or all those not 0

        Args:
            search: key value pairs that must be contained
            display: optional, extract keys from the retrieved dictionary to be returned

        Returns:
            list of dictionaries fulfilling search and display criteria

        Example:
            find_in_list_of_dict(search: {'ID': '1EC21030423', "nombreFactura": "IMM HARMONIE CREAM 50ML"},
                                display: {"presentacionComercial": 1})
            [{"presentacionComercial": "COS-512498"}]
        """

        results = []
        for elem in (dict(line) for line in self.data):
            if all([elem.get(k, None) == v for k, v in search.items()]):
                if display:
                    if sum(display.values()) > 0:  # display has elements with 1, defining what to show
                        reduced_elem = {k: v for k, v in elem.items() if display.get(k, None) == 1}
                    else:  # display has elements with 0, thus defining what not to show
                        reduced_elem = {k: v for k, v in elem.items() if display.get(k, None) != 0}
                    results.append(reduced_elem)
                else:
                    results.append(elem)
        return results

    @property
    def last_update(self) -> str:
        """Date and time of the last change to the storage file.

        Returns:
            String in the format: 13 Feb 2025 - 15:09 (UTC)
        """
        timestamp = self.filehandler.last_modification
        d = datetime.fromtimestamp(timestamp).astimezone(ZoneInfo('UTC')).strftime('%d %b %Y - %H:%M')
        return d
