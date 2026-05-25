# ./planner.py

import random
from urllib.parse import quote

from constants import (
    PLACES_PER_DAY_BY_PACE,
    SCOPE_FILTER_MAP,
    TIME_ORDER,
    TRIP_STYLE_TAG_WEIGHTS,
    VARIATION_STRENGTH_BY_MODE,
)


PLACE_TYPE_MATCH_SCORE = 8


def build_trip_style_tag_weights(selected_trip_style: str) -> dict[str, int]:
    return TRIP_STYLE_TAG_WEIGHTS.get(selected_trip_style, {})


def calculate_place_score(
    place: dict,
    selected_preferences: list[str],
    selected_trip_style: str,
    selected_place_types: list[str] | None = None,
) -> int:
    place_tags = set(place["tags"])
    matched_tag_count = len(place_tags & set(selected_preferences))

    final_score = place["score"] + matched_tag_count * 3
    trip_style_tag_weights = build_trip_style_tag_weights(selected_trip_style)

    for tag, weight in trip_style_tag_weights.items():
        if tag in place_tags:
            final_score += weight

    if selected_place_types and place.get("place_type") in set(selected_place_types):
        final_score += PLACE_TYPE_MATCH_SCORE

    return final_score


def calculate_weather_score_adjustment(place: dict, weather_mode: str) -> int:
    place_tags = set(place["tags"])

    if weather_mode == "正常天气":
        return 0

    if weather_mode == "下雨":
        adjustment_score = 0

        if "室内" in place_tags:
            adjustment_score += 5

        if "购物" in place_tags:
            adjustment_score += 3

        if "美食" in place_tags:
            adjustment_score += 2

        if "历史文化" in place_tags:
            adjustment_score += 2

        if "自然风景" in place_tags:
            adjustment_score -= 4

        if "夜景" in place_tags:
            adjustment_score -= 2

        return adjustment_score

    if weather_mode == "炎热":
        adjustment_score = 0

        if "室内" in place_tags:
            adjustment_score += 4

        if "购物" in place_tags:
            adjustment_score += 3

        if "自然风景" in place_tags:
            adjustment_score -= 2

        if "轻松" in place_tags:
            adjustment_score += 2

        return adjustment_score

    return 0


def build_amap_search_url(city_name: str, place_name: str) -> str:
    keyword = quote(f"{city_name} {place_name}")
    return f"https://www.amap.com/search?query={keyword}"


def get_place_route_group(place: dict) -> str:
    return place.get("route_group", place["area"])


def build_scored_places(
    city_data: dict,
    selected_preferences: list[str],
    selected_trip_style: str,
    generation_mode: str,
    route_version: int,
    weather_mode: str,
    required_place_names: list[str],
    excluded_place_names: list[str],
    selected_place_types: list[str] | None = None,
) -> list[dict]:
    city_name = city_data["city"]
    scored_places = []
    random_generator = random.Random(route_version)
    variation_strength = VARIATION_STRENGTH_BY_MODE.get(generation_mode, 0)
    required_place_name_set = set(required_place_names)
    excluded_place_name_set = set(excluded_place_names)

    for place in city_data["places"]:
        if place["name"] in excluded_place_name_set:
            continue

        place_with_score = place.copy()
        final_score = calculate_place_score(
            place,
            selected_preferences,
            selected_trip_style,
            selected_place_types,
        )

        final_score += calculate_weather_score_adjustment(
            place,
            weather_mode,
        )

        if variation_strength > 0:
            final_score += random_generator.randint(
                -variation_strength,
                variation_strength,
            )

        if place["name"] in required_place_name_set:
            final_score += 100

        place_with_score["final_score"] = max(0, final_score)
        place_with_score["amap_url"] = build_amap_search_url(city_name, place["name"])
        scored_places.append(place_with_score)

    return scored_places


def filter_places_by_travel_scope(
    scored_places: list[dict],
    selected_travel_scope: str,
    required_place_names: list[str],
) -> list[dict]:
    allowed_travel_scopes = SCOPE_FILTER_MAP.get(selected_travel_scope)

    if not allowed_travel_scopes:
        return scored_places

    required_place_name_set = set(required_place_names)

    filtered_scored_places = [
        place
        for place in scored_places
        if (
            place.get("travel_scope", "市区") in allowed_travel_scopes
            or place["name"] in required_place_name_set
        )
    ]

    if filtered_scored_places:
        return filtered_scored_places

    return scored_places


def group_places_by_route_group(scored_places: list[dict]) -> dict[str, list[dict]]:
    places_by_area = {}

    for place in scored_places:
        route_group_name = get_place_route_group(place)

        if route_group_name not in places_by_area:
            places_by_area[route_group_name] = []

        places_by_area[route_group_name].append(place)

    return places_by_area


def build_area_plans(scored_places: list[dict]) -> list[dict]:
    places_by_area = group_places_by_route_group(scored_places)
    area_plans = []

    for area_name, area_places in places_by_area.items():
        sorted_area_places = sorted(
            area_places,
            key=lambda place: place["final_score"],
            reverse=True,
        )

        area_score = sum(place["final_score"] for place in sorted_area_places[:4])

        area_plans.append(
            {
                "area": area_name,
                "score": area_score,
                "places": sorted_area_places,
            }
        )

    return sorted(
        area_plans,
        key=lambda area_plan: area_plan["score"],
        reverse=True,
    )


def build_candidate_places_for_day(
    day_index: int,
    sorted_area_plans: list[dict],
    scored_places: list[dict],
) -> tuple[str, list[dict]]:
    if day_index < len(sorted_area_plans):
        selected_area_plan = sorted_area_plans[day_index]
        return selected_area_plan["area"], selected_area_plan["places"]

    return "综合路线", sorted(
        scored_places,
        key=lambda place: place["final_score"],
        reverse=True,
    )


def select_day_places(
    candidate_places: list[dict],
    scored_places: list[dict],
    used_place_names: set[str],
    places_per_day: int,
) -> list[dict]:
    day_places = []

    for place in candidate_places:
        if place["name"] in used_place_names:
            continue

        day_places.append(place)
        used_place_names.add(place["name"])

        if len(day_places) >= places_per_day:
            return day_places

    remaining_places = sorted(
        [
            place
            for place in scored_places
            if place["name"] not in used_place_names
        ],
        key=lambda place: place["final_score"],
        reverse=True,
    )

    for place in remaining_places:
        day_places.append(place)
        used_place_names.add(place["name"])

        if len(day_places) >= places_per_day:
            break

    return day_places


def order_day_places(day_places: list[dict]) -> list[dict]:
    return sorted(
        day_places,
        key=lambda place: (
            TIME_ORDER.get(place["best_time"], 99),
            place.get("route_order", 999),
            -place["final_score"],
        ),
    )


def build_selected_place_names(trip_plan: list[dict]) -> set[str]:
    return {
        place["name"]
        for day_plan in trip_plan
        for place in day_plan["places"]
    }


def find_append_day_index(
    required_place: dict,
    trip_plan: list[dict],
    places_per_day: int,
) -> int | None:
    required_route_group = get_place_route_group(required_place)
    append_candidates = []

    for day_index, day_plan in enumerate(trip_plan):
        day_places = day_plan["places"]

        if len(day_places) >= places_per_day:
            continue

        same_route_group_count = sum(
            1
            for place in day_places
            if get_place_route_group(place) == required_route_group
        )

        append_candidates.append(
            {
                "day_index": day_index,
                "same_route_group_count": same_route_group_count,
                "place_count": len(day_places),
            }
        )

    if not append_candidates:
        return None

    best_append_candidate = max(
        append_candidates,
        key=lambda candidate: (
            candidate["same_route_group_count"],
            -candidate["place_count"],
        ),
    )

    return best_append_candidate["day_index"]


def find_replacement_position(
    required_place: dict,
    trip_plan: list[dict],
    required_place_names: list[str],
) -> tuple[int, int] | None:
    required_route_group = get_place_route_group(required_place)
    required_place_name_set = set(required_place_names)
    replacement_candidates = []

    for day_index, day_plan in enumerate(trip_plan):
        day_places = day_plan["places"]
        same_route_group_count = sum(
            1
            for place in day_places
            if get_place_route_group(place) == required_route_group
        )

        for place_index, place in enumerate(day_places):
            if place["name"] in required_place_name_set:
                continue

            replacement_candidates.append(
                {
                    "day_index": day_index,
                    "place_index": place_index,
                    "same_route_group_count": same_route_group_count,
                    "replaced_place_score": place["final_score"],
                }
            )

    if not replacement_candidates:
        return None

    best_replacement_candidate = max(
        replacement_candidates,
        key=lambda candidate: (
            candidate["same_route_group_count"],
            -candidate["replaced_place_score"],
        ),
    )

    return (
        best_replacement_candidate["day_index"],
        best_replacement_candidate["place_index"],
    )


def apply_required_place_constraint(
    trip_plan: list[dict],
    scored_places: list[dict],
    required_place_names: list[str],
    places_per_day: int,
) -> list[dict]:
    if not required_place_names:
        return trip_plan

    places_by_name = {
        place["name"]: place
        for place in scored_places
    }

    selected_place_names = build_selected_place_names(trip_plan)

    for required_place_name in required_place_names:
        if required_place_name in selected_place_names:
            continue

        required_place = places_by_name.get(required_place_name)

        if not required_place:
            continue

        append_day_index = find_append_day_index(
            required_place,
            trip_plan,
            places_per_day,
        )

        if append_day_index is not None:
            trip_plan[append_day_index]["places"].append(required_place)
            selected_place_names.add(required_place_name)
            continue

        replacement_position = find_replacement_position(
            required_place,
            trip_plan,
            required_place_names,
        )

        if replacement_position is None:
            continue

        replacement_day_index, replacement_place_index = replacement_position
        replaced_place = trip_plan[replacement_day_index]["places"][replacement_place_index]
        trip_plan[replacement_day_index]["places"][replacement_place_index] = required_place
        selected_place_names.discard(replaced_place["name"])
        selected_place_names.add(required_place_name)

    for day_plan in trip_plan:
        day_plan["places"] = order_day_places(day_plan["places"])

    return trip_plan


def generate_trip_plan(
    city_data: dict,
    travel_days: int,
    selected_preferences: list[str],
    selected_travel_scope: str,
    travel_pace: str,
    selected_trip_style: str,
    generation_mode: str,
    route_version: int,
    weather_mode: str,
    required_place_names: list[str],
    excluded_place_names: list[str],
    selected_place_types: list[str] | None = None,
) -> list[dict]:
    scored_places = build_scored_places(
        city_data,
        selected_preferences,
        selected_trip_style,
        generation_mode,
        route_version,
        weather_mode,
        required_place_names,
        excluded_place_names,
        selected_place_types,
    )

    scored_places = filter_places_by_travel_scope(
        scored_places,
        selected_travel_scope,
        required_place_names,
    )

    sorted_area_plans = build_area_plans(scored_places)
    places_per_day = PLACES_PER_DAY_BY_PACE.get(travel_pace, 4)
    trip_plan = []
    used_place_names = set()

    for day_index in range(travel_days):
        day_area, candidate_places = build_candidate_places_for_day(
            day_index,
            sorted_area_plans,
            scored_places,
        )

        day_places = select_day_places(
            candidate_places,
            scored_places,
            used_place_names,
            places_per_day,
        )

        trip_plan.append(
            {
                "day": day_index + 1,
                "area": day_area,
                "places": order_day_places(day_places),
            }
        )

    return apply_required_place_constraint(
        trip_plan,
        scored_places,
        required_place_names,
        places_per_day,
    )