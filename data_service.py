# ./data_service.py

import json
from pathlib import Path

from constants import (
    DATA_TRAVEL_SCOPE_AROUND,
    DATA_TRAVEL_SCOPE_CITY,
    DATA_TRAVEL_SCOPE_FAR,
    TRAVEL_SCOPE_ALL,
    TRAVEL_SCOPE_CITY_AND_AROUND,
    TRAVEL_SCOPE_CITY_ONLY,
    TRAVEL_SCOPE_FAR_NATURE,
)


DATA_DIRECTORY = Path(__file__).parent / "data"


def load_city_options() -> dict[str, str]:
    city_options = {}

    for city_file_path in sorted(DATA_DIRECTORY.glob("*.json")):
        with city_file_path.open("r", encoding="utf-8") as city_file:
            city_data = json.load(city_file)

        city_name = city_data.get("city")

        if not city_name:
            continue

        city_options[city_name] = city_file_path.name

    return city_options


def load_city_data(city_file_name: str) -> dict:
    file_path = DATA_DIRECTORY / city_file_name

    with file_path.open("r", encoding="utf-8") as city_file:
        return json.load(city_file)


def build_travel_scope_options(city_data: dict) -> list[str]:
    existing_travel_scopes = {
        place.get("travel_scope", DATA_TRAVEL_SCOPE_CITY)
        for place in city_data["places"]
    }

    travel_scope_options = [TRAVEL_SCOPE_ALL]

    if DATA_TRAVEL_SCOPE_CITY in existing_travel_scopes:
        travel_scope_options.append(TRAVEL_SCOPE_CITY_ONLY)

    if DATA_TRAVEL_SCOPE_AROUND in existing_travel_scopes:
        travel_scope_options.append(TRAVEL_SCOPE_CITY_AND_AROUND)

    if DATA_TRAVEL_SCOPE_FAR in existing_travel_scopes:
        travel_scope_options.append(TRAVEL_SCOPE_FAR_NATURE)

    return travel_scope_options