# ./export_service.py

from constants import BEST_TIME_OPTIONS
from quality import build_day_quality_score, build_day_summary


def build_trip_markdown(
    selected_city: str,
    travel_days: int,
    travel_pace: str,
    selected_trip_style: str,
    generation_mode: str,
    weather_mode: str,
    route_version: int,
    selected_preferences: list[str],
    selected_travel_scope: str,
    required_place_names: list[str],
    excluded_place_names: list[str],
    trip_plan: list[dict],
) -> str:
    markdown_lines = []

    markdown_lines.append(f"# {selected_city} {travel_days} 天游玩路线")
    markdown_lines.append("")
    markdown_lines.append("## 路线条件")
    markdown_lines.append("")
    markdown_lines.append(f"- 城市：{selected_city}")
    markdown_lines.append(f"- 旅行天数：{travel_days} 天")
    markdown_lines.append(f"- 旅行节奏：{travel_pace}")
    markdown_lines.append(f"- 路线风格：{selected_trip_style}")
    markdown_lines.append(f"- 路线范围：{selected_travel_scope}")
    markdown_lines.append(f"- 天气情况：{weather_mode}")
    markdown_lines.append(f"- 生成变化：{generation_mode}")
    markdown_lines.append(f"- 路线版本：第 {route_version} 版")

    if selected_preferences:
        markdown_lines.append(f"- 旅行偏好：{'、'.join(selected_preferences)}")

    if required_place_names:
        markdown_lines.append(f"- 必去景点：{'、'.join(required_place_names)}")

    if excluded_place_names:
        markdown_lines.append(f"- 已排除景点：{'、'.join(excluded_place_names)}")

    markdown_lines.append("")

    for day_plan in trip_plan:
        markdown_lines.append(f"## 第 {day_plan['day']} 天：{day_plan['area']}路线")
        markdown_lines.append("")
        markdown_lines.append(build_day_summary(day_plan))
        markdown_lines.append("")

        quality_score_result = build_day_quality_score(
            day_plan,
            selected_preferences,
            travel_pace,
        )

        markdown_lines.append(f"路线评分：{quality_score_result['score']} / 100")
        markdown_lines.append("")

        route_text = " → ".join(place["name"] for place in day_plan["places"])
        markdown_lines.append(f"路线：{route_text}")
        markdown_lines.append("")

        for section_name in BEST_TIME_OPTIONS:
            section_places = [
                place
                for place in day_plan["places"]
                if place["best_time"] == section_name
            ]

            if not section_places:
                continue

            markdown_lines.append(f"### {section_name}")
            markdown_lines.append("")

            for place in section_places:
                markdown_lines.append(f"#### {place['name']}")
                markdown_lines.append("")
                markdown_lines.append(f"- 类型：{place['place_type']}")
                markdown_lines.append(f"- 区域：{place['area']}")
                markdown_lines.append(f"- 推荐时间：{place['best_time']}")
                markdown_lines.append(f"- 建议停留：{place['duration_minutes']} 分钟")
                markdown_lines.append(f"- 推荐理由：{place['description']}")
                markdown_lines.append(f"- 高德地图：{place['amap_url']}")

        markdown_lines.append("---")
        markdown_lines.append("")

    return "\n".join(markdown_lines)


def build_trip_file_name(
    selected_city: str,
    travel_days: int,
    travel_pace: str,
    selected_trip_style: str,
) -> str:
    return f"{selected_city}_{travel_days}天_{travel_pace}_{selected_trip_style}_旅游路线.md"