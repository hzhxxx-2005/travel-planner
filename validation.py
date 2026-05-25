# ./validation.py

from constants import (
    PLACES_PER_DAY_BY_PACE,
    SCOPE_FILTER_MAP,
)


def get_places_per_day(travel_pace: str) -> int:
    return PLACES_PER_DAY_BY_PACE.get(travel_pace, 4)


def build_allowed_travel_scopes(selected_travel_scope: str) -> set[str] | None:
    return SCOPE_FILTER_MAP.get(selected_travel_scope)


def validate_trip_conditions(
    city_data: dict,
    travel_days: int,
    travel_pace: str,
    selected_travel_scope: str,
    required_place_names: list[str],
    excluded_place_names: list[str],
) -> list[str]:
    warnings = []

    required_place_name_set = set(required_place_names)
    excluded_place_name_set = set(excluded_place_names)

    repeated_place_names = required_place_name_set & excluded_place_name_set

    for place_name in sorted(repeated_place_names):
        warnings.append(f"“{place_name}”同时出现在必去景点和不想去景点中。")

    places_by_name = {
        place["name"]: place
        for place in city_data["places"]
    }

    allowed_travel_scopes = build_allowed_travel_scopes(selected_travel_scope)

    if allowed_travel_scopes:
        for place_name in required_place_names:
            place = places_by_name.get(place_name)

            if not place:
                continue

            place_travel_scope = place.get("travel_scope", "市区")

            if place_travel_scope not in allowed_travel_scopes:
                warnings.append(
                    f"必去景点“{place_name}”属于“{place_travel_scope}”，"
                    f"但当前路线范围是“{selected_travel_scope}”。"
                )

    places_per_day = get_places_per_day(travel_pace)
    max_place_count = travel_days * places_per_day

    if len(required_place_names) > max_place_count:
        warnings.append(
            f"当前 {travel_days} 天、{travel_pace}节奏大约最多安排 {max_place_count} 个地点，"
            f"但你选择了 {len(required_place_names)} 个必去景点。"
        )

    available_places = [
        place
        for place in city_data["places"]
        if place["name"] not in excluded_place_name_set
    ]

    if allowed_travel_scopes:
        available_places = [
            place
            for place in available_places
            if place.get("travel_scope", "市区") in allowed_travel_scopes
        ]

    if len(available_places) < max_place_count:
        warnings.append(
            f"当前筛选条件下可用地点只有 {len(available_places)} 个，"
            f"少于预计安排的 {max_place_count} 个地点，路线可能不完整。"
        )

    return warnings