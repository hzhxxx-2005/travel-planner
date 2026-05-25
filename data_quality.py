# ./data_quality.py

from typing import Any

from constants import (
    BEST_TIME_OPTIONS,
    DATA_TRAVEL_SCOPE_CITY,
    DATA_TRAVEL_SCOPE_OPTIONS,
    PLACE_TYPE_OPTIONS,
    REQUIRED_JSON_PLACE_FIELD_NAMES,
    SUPPORTED_TAGS,
)


def is_positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def build_city_data_quality_report(city_data: dict, city_file_name: str = "") -> dict:
    errors = []
    warnings = []

    if not isinstance(city_data, dict):
        return {
            "errors": ["城市数据顶层结构必须是对象。"],
            "warnings": [],
            "error_count": 1,
            "warning_count": 0,
        }

    city_name = city_data.get("city")

    if not isinstance(city_name, str) or not city_name.strip():
        errors.append("city 必须是非空字符串。")
        city_name = ""

    places = city_data.get("places")

    if not isinstance(places, list):
        errors.append("places 必须是列表。")
        return {
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
        }

    if not places:
        errors.append("places 不能为空。")
        return {
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
        }

    required_field_name_set = set(REQUIRED_JSON_PLACE_FIELD_NAMES)
    allowed_best_time_set = set(BEST_TIME_OPTIONS)
    allowed_travel_scope_set = set(DATA_TRAVEL_SCOPE_OPTIONS)
    allowed_place_type_set = set(PLACE_TYPE_OPTIONS)
    supported_tag_set = set(SUPPORTED_TAGS)
    seen_place_names = set()

    for place_index, place in enumerate(places):
        item_prefix = f"{city_file_name or city_name} places[{place_index}]"

        if not isinstance(place, dict):
            errors.append(f"{item_prefix}：地点必须是对象。")
            continue

        missing_field_names = required_field_name_set - set(place.keys())

        if missing_field_names:
            errors.append(f"{item_prefix}：缺少必要字段：{sorted(missing_field_names)}")

        place_name = place.get("name")

        if isinstance(place_name, str) and place_name.strip():
            display_place_name = place_name.strip()
            place_key = (city_name, display_place_name)

            if place_key in seen_place_names:
                errors.append(f"{item_prefix}：同一个城市内景点重复：{display_place_name}")
            else:
                seen_place_names.add(place_key)
        else:
            display_place_name = f"第 {place_index + 1} 个地点"

        display_prefix = f"地点“{display_place_name}”"

        for string_field_name in ["name", "place_type", "area", "route_group", "description"]:
            if string_field_name not in place:
                continue

            field_value = place.get(string_field_name)

            if not isinstance(field_value, str) or not field_value.strip():
                errors.append(f"{display_prefix}：{string_field_name} 必须是非空字符串。")

        place_type = place.get("place_type")

        if "place_type" in place and place_type not in allowed_place_type_set:
            errors.append(
                f"{display_prefix}：place_type 必须是 "
                f"{' / '.join(PLACE_TYPE_OPTIONS)}，当前是：{place_type}"
            )

        route_order = place.get("route_order")

        if "route_order" in place and not is_positive_integer(route_order):
            errors.append(f"{display_prefix}：route_order 必须是正整数。")

        duration_minutes = place.get("duration_minutes")

        if "duration_minutes" in place and not is_positive_integer(duration_minutes):
            errors.append(f"{display_prefix}：duration_minutes 必须是正整数。")

        score = place.get("score")

        if "score" in place and not is_positive_integer(score):
            errors.append(f"{display_prefix}：score 必须是正整数。")
        elif isinstance(score, int) and not isinstance(score, bool) and score > 10:
            warnings.append(f"{display_prefix}：score 建议在 1 到 10 之间，当前是：{score}")

        best_time = place.get("best_time")

        if "best_time" in place and best_time not in allowed_best_time_set:
            errors.append(
                f"{display_prefix}：best_time 必须是 "
                f"{' / '.join(BEST_TIME_OPTIONS)}，当前是：{best_time}"
            )

        tags = place.get("tags")

        if "tags" in place:
            if not isinstance(tags, list):
                errors.append(f"{display_prefix}：tags 必须是列表。")
            elif not tags:
                errors.append(f"{display_prefix}：tags 不能为空。")
            else:
                for tag in tags:
                    if not isinstance(tag, str) or not tag.strip():
                        errors.append(f"{display_prefix}：tags 包含空标签或非字符串标签。")
                        continue

                    if tag not in supported_tag_set:
                        warnings.append(f"{display_prefix}：发现未登记标签：{tag}")

        travel_scope = place.get("travel_scope", DATA_TRAVEL_SCOPE_CITY)

        if not isinstance(travel_scope, str):
            errors.append(f"{display_prefix}：travel_scope 必须是字符串。")
        elif not travel_scope.strip():
            errors.append(f"{display_prefix}：travel_scope 不能为空。")
        elif travel_scope not in allowed_travel_scope_set:
            errors.append(
                f"{display_prefix}：travel_scope 必须是 "
                f"{' / '.join(DATA_TRAVEL_SCOPE_OPTIONS)}，当前是：{travel_scope}"
            )

    return {
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
    }