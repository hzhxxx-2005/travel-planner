# ./quality.py

from constants import PACE_DURATION_RANGES


def build_day_summary(day_plan: dict) -> str:
    places = day_plan["places"]

    if not places:
        return "当前数据不足，暂时无法生成这一天的路线说明。"

    route_name = day_plan["area"]

    morning_places = [place["name"] for place in places if place["best_time"] == "上午"]
    afternoon_places = [place["name"] for place in places if place["best_time"] == "下午"]
    evening_places = [place["name"] for place in places if place["best_time"] == "晚上"]

    tag_count = {}

    for place in places:
        for tag in place["tags"]:
            tag_count[tag] = tag_count.get(tag, 0) + 1

    main_tags = [
        tag
        for tag, _ in sorted(
            tag_count.items(),
            key=lambda tag_item: tag_item[1],
            reverse=True,
        )[:3]
    ]

    summary_parts = [f"这一天建议走{route_name}。"]

    if morning_places:
        summary_parts.append(f"上午可以先去{'、'.join(morning_places)}。")

    if afternoon_places:
        summary_parts.append(f"下午安排{'、'.join(afternoon_places)}。")

    if evening_places:
        summary_parts.append(f"晚上适合去{'、'.join(evening_places)}。")

    if main_tags:
        summary_parts.append(f"整体偏向{'、'.join(main_tags)}。")

    return "".join(summary_parts)


def build_day_quality_notes(day_plan: dict) -> list[str]:
    places = day_plan["places"]
    notes = []

    if not places:
        return ["当前数据不足，无法判断路线质量。"]

    total_duration_minutes = sum(place["duration_minutes"] for place in places)

    morning_place_count = len([
        place
        for place in places
        if place["best_time"] == "上午"
    ])

    afternoon_place_count = len([
        place
        for place in places
        if place["best_time"] == "下午"
    ])

    evening_place_count = len([
        place
        for place in places
        if place["best_time"] == "晚上"
    ])

    route_group_count = len({
        place.get("route_group", place["area"])
        for place in places
    })

    if total_duration_minutes > 540:
        notes.append("这一天的预计游玩时间较长，适合特种兵节奏。")

    if total_duration_minutes < 240:
        notes.append("这一天的安排偏轻松，可以补充一个附近景点或增加休息时间。")

    if morning_place_count == 0:
        notes.append("这一天缺少上午景点，实际使用时可以把第一个下午景点提前到上午。")

    if afternoon_place_count == 0:
        notes.append("这一天缺少下午景点，路线可能不够完整。")

    if evening_place_count == 0:
        notes.append("这一天没有安排夜间活动，适合想早点休息的用户。")

    if route_group_count > 1:
        notes.append("这一天包含多个路线组，可能是为了补足景点数量，实际游玩前建议检查距离。")

    return notes


def build_day_quality_score(
    day_plan: dict,
    selected_preferences: list[str],
    travel_pace: str,
) -> dict:
    places = day_plan["places"]

    if not places:
        return {
            "score": 0,
            "advantages": [],
            "risks": ["当前数据不足，无法计算路线评分。"],
        }

    score = 60
    advantages = []
    risks = []

    total_duration_minutes = sum(place["duration_minutes"] for place in places)

    existing_time_sections = {
        place["best_time"]
        for place in places
    }

    route_group_names = {
        place.get("route_group", place["area"])
        for place in places
    }

    matched_preference_count = 0

    for place in places:
        matched_preference_count += len(set(place["tags"]) & set(selected_preferences))

    min_duration_minutes, max_duration_minutes = PACE_DURATION_RANGES.get(
        travel_pace,
        (300, 480),
    )

    if len(existing_time_sections) >= 3:
        score += 10
        advantages.append("上午、下午、晚上都有安排，时间段比较完整。")
    elif len(existing_time_sections) == 2:
        score += 5
        advantages.append("路线覆盖了两个主要时间段，整体安排基本完整。")
    else:
        score -= 8
        risks.append("这一天的时间段比较单一，可能不像完整的一日游路线。")

    if len(route_group_names) == 1:
        score += 15
        advantages.append("当天地点集中在同一条路线组内，路线顺路性较好。")
    elif len(route_group_names) == 2:
        score += 5
        advantages.append("当天包含两个路线组，整体仍然可以接受。")
    else:
        score -= 10
        risks.append("当天包含多个路线组，实际游玩前建议检查地点距离。")

    if matched_preference_count >= 5:
        score += 10
        advantages.append("路线和用户偏好匹配度较高。")
    elif matched_preference_count >= 2:
        score += 5
        advantages.append("路线和用户偏好有一定匹配。")
    else:
        score -= 5
        risks.append("路线和当前偏好匹配较弱，可以尝试调整偏好或补充数据。")

    if min_duration_minutes <= total_duration_minutes <= max_duration_minutes:
        score += 10
        advantages.append(f"预计游玩时长适合{travel_pace}节奏。")
    elif total_duration_minutes < min_duration_minutes:
        score -= 5
        risks.append("当天预计游玩时间偏短，可能显得安排较空。")
    else:
        score -= 8
        risks.append("当天预计游玩时间偏长，实际体验可能偏赶。")

    if not risks:
        risks.append("暂无明显风险。")

    final_score = max(0, min(100, score))

    return {
        "score": final_score,
        "advantages": advantages,
        "risks": risks,
    }