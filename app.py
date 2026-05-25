# ./app.py

import streamlit as st

from constants import (
    BEST_TIME_OPTIONS,
    DEFAULT_PREFERENCE_OPTIONS,
    DEFAULT_SELECTED_PREFERENCES,
    GENERATION_MODE_OPTIONS,
    PLACE_TYPE_OPTIONS,
    TRAVEL_PACE_OPTIONS,
    TRIP_STYLE_OPTIONS,
    WEATHER_MODE_OPTIONS,
)
from data_service import (
    build_travel_scope_options,
    load_city_data,
    load_city_options,
)
from export_service import build_trip_file_name, build_trip_markdown
from planner import generate_trip_plan
from quality import (
    build_day_quality_notes,
    build_day_quality_score,
    build_day_summary,
)
from validation import validate_trip_conditions
from data_quality import build_city_data_quality_report

st.set_page_config(
    page_title="中国境内旅游路线生成器",
    page_icon="🧭",
    layout="centered",
)

st.title("中国境内旅游路线生成器")
st.write("在左侧选择旅行条件，生成一份可复制的简易旅游路线。")

st.divider()

with st.sidebar:
    st.header("路线条件")

    city_options = load_city_options()

    if not city_options:
        st.error("没有找到城市数据，请先运行 python tools/csv_to_json.py 生成 JSON 文件。")
        st.stop()

    selected_city = st.selectbox("选择城市", list(city_options.keys()))

    city_data = load_city_data(city_options[selected_city])
    data_quality_report = build_city_data_quality_report(
        city_data,
        city_options[selected_city],
    )

    if data_quality_report["error_count"] > 0:
        st.error(
            f"当前城市数据存在 {data_quality_report['error_count']} 个错误，"
            f"请先修复数据后再生成路线。"
        )

        with st.expander("查看数据错误", expanded=True):
            for data_error in data_quality_report["errors"]:
                st.write(f"- {data_error}")

        st.stop()

    if data_quality_report["warning_count"] > 0:
        with st.expander(
            f"数据质量提醒：{data_quality_report['warning_count']} 项",
            expanded=False,
        ):
            for data_warning in data_quality_report["warnings"]:
                st.write(f"- {data_warning}")
    available_place_count = len(city_data["places"])
    available_route_group_count = len({
        place.get("route_group", place["area"])
        for place in city_data["places"]
    })

    st.caption(
        f"当前城市已收录 {available_place_count} 个地点，"
        f"{available_route_group_count} 条路线组。"
    )

    travel_scope_options = build_travel_scope_options(city_data)

    selected_travel_scope = st.selectbox(
        "路线范围",
        travel_scope_options,
    )

    travel_days = st.slider(
        "旅行天数",
        min_value=1,
        max_value=3,
        value=2,
    )

    travel_pace = st.selectbox(
        "旅行节奏",
        list(TRAVEL_PACE_OPTIONS),
        index=1,
    )

    selected_trip_style = st.selectbox(
        "路线风格",
        list(TRIP_STYLE_OPTIONS),
    )

    generation_mode = st.selectbox(
        "生成变化",
        list(GENERATION_MODE_OPTIONS),
    )

    weather_mode = st.selectbox(
        "天气情况",
        list(WEATHER_MODE_OPTIONS),
    )

    if "route_version" not in st.session_state:
        st.session_state["route_version"] = 1

    if "trip_plan" not in st.session_state:
        st.session_state["trip_plan"] = None

    if "trip_context" not in st.session_state:
        st.session_state["trip_context"] = None

    if "trip_history" not in st.session_state:
        st.session_state["trip_history"] = []

    st.caption(f"当前路线版本：第 {st.session_state['route_version']} 版")

    selected_preferences = st.multiselect(
        "选择旅行偏好",
        list(DEFAULT_PREFERENCE_OPTIONS),
        default=list(DEFAULT_SELECTED_PREFERENCES),
    )
    selected_place_types = st.multiselect(
        "地点类型偏好",
        list(PLACE_TYPE_OPTIONS),
    )
    place_name_options = [
        place["name"]
        for place in city_data["places"]
    ]

    required_place_names = st.multiselect(
        "必去景点",
        place_name_options,
    )

    excluded_place_names = st.multiselect(
        "不想去景点",
        [
            place_name
            for place_name in place_name_options
            if place_name not in required_place_names
        ],
    )

    generate_button_clicked = st.button("生成路线", use_container_width=True)
    regenerate_button_clicked = st.button("重新生成一版", use_container_width=True)

    if st.session_state["trip_history"]:
        history_labels = [
            history_item["label"]
            for history_item in st.session_state["trip_history"]
        ]

        selected_history_label = st.selectbox(
            "历史路线版本",
            history_labels,
            index=len(history_labels) - 1,
        )

        selected_history_index = history_labels.index(selected_history_label)
        selected_history_item = st.session_state["trip_history"][selected_history_index]

        if st.button("查看选中历史版本", use_container_width=True):
            st.session_state["trip_plan"] = selected_history_item["trip_plan"]
            st.session_state["trip_context"] = selected_history_item["trip_context"]

        if st.button("清空历史路线", use_container_width=True):
            st.session_state["trip_history"] = []
            st.session_state["trip_plan"] = None
            st.session_state["trip_context"] = None

current_input_context = {
    "selected_city": selected_city,
    "travel_days": travel_days,
    "travel_pace": travel_pace,
    "selected_trip_style": selected_trip_style,
    "generation_mode": generation_mode,
    "weather_mode": weather_mode,
    "selected_preferences": selected_preferences,
    "selected_place_types": selected_place_types,
    "selected_travel_scope": selected_travel_scope,
    "required_place_names": required_place_names,
    "excluded_place_names": excluded_place_names,
}

if regenerate_button_clicked:
    st.session_state["route_version"] += 1

if generate_button_clicked or regenerate_button_clicked:
    condition_warnings = validate_trip_conditions(
        city_data,
        travel_days,
        travel_pace,
        selected_travel_scope,
        required_place_names,
        excluded_place_names,
    )

    trip_plan = generate_trip_plan(
        city_data,
        travel_days,
        selected_preferences,
        selected_travel_scope,
        travel_pace,
        selected_trip_style,
        generation_mode,
        st.session_state["route_version"],
        weather_mode,
        required_place_names,
        excluded_place_names,
        selected_place_types,
    )

    trip_context = {
        "selected_city": selected_city,
        "travel_days": travel_days,
        "travel_pace": travel_pace,
        "selected_trip_style": selected_trip_style,
        "generation_mode": generation_mode,
        "weather_mode": weather_mode,
        "route_version": st.session_state["route_version"],
        "selected_preferences": selected_preferences,
        "selected_place_types": selected_place_types,
        "selected_travel_scope": selected_travel_scope,
        "required_place_names": required_place_names,
        "excluded_place_names": excluded_place_names,
        "condition_warnings": condition_warnings,
        "input_context": current_input_context,
    }

    st.session_state["trip_plan"] = trip_plan
    st.session_state["trip_context"] = trip_context

    st.session_state["trip_history"].append(
        {
            "label": (
                f"第 {trip_context['route_version']} 版｜"
                f"{trip_context['selected_city']}｜"
                f"{trip_context['travel_pace']}节奏｜"
                f"{trip_context['selected_trip_style']}"
            ),
            "trip_plan": trip_plan,
            "trip_context": trip_context,
        }
    )

if st.session_state["trip_plan"] is not None:
    trip_plan = st.session_state["trip_plan"]
    trip_context = st.session_state["trip_context"]

    saved_input_context = trip_context.get("input_context")

    if saved_input_context != current_input_context:
        st.warning("路线条件已变更，请重新点击“生成路线”。")
        st.stop()

    selected_city = trip_context["selected_city"]
    travel_days = trip_context["travel_days"]
    travel_pace = trip_context["travel_pace"]
    selected_trip_style = trip_context["selected_trip_style"]
    generation_mode = trip_context["generation_mode"]
    weather_mode = trip_context["weather_mode"]
    route_version = trip_context["route_version"]
    selected_preferences = trip_context["selected_preferences"]
    selected_place_types = trip_context.get("selected_place_types", [])
    selected_travel_scope = trip_context["selected_travel_scope"]
    required_place_names = trip_context["required_place_names"]
    excluded_place_names = trip_context["excluded_place_names"]
    condition_warnings = trip_context["condition_warnings"]

    st.subheader(
        f"{selected_city} {travel_days} 天游玩路线｜"
        f"{travel_pace}节奏｜{selected_trip_style}｜{generation_mode}｜"
        f"{weather_mode}｜第 {route_version} 版"
    )
    if selected_place_types:
        st.caption(f"地点类型偏好：{'、'.join(selected_place_types)}")
    if required_place_names:
        st.caption(f"必去景点：{'、'.join(required_place_names)}")

    if excluded_place_names:
        st.caption(f"已排除景点：{'、'.join(excluded_place_names)}")

    for warning in condition_warnings:
        st.warning(warning)

    for day_plan in trip_plan:
        with st.container(border=True):
            st.markdown(f"## 第 {day_plan['day']} 天｜{day_plan['area']}路线")

            if not day_plan["places"]:
                st.warning("当前数据不足，无法生成这一天的路线。")
                continue

            day_summary = build_day_summary(day_plan)
            st.write(day_summary)

            quality_score_result = build_day_quality_score(
                day_plan,
                selected_preferences,
                travel_pace,
            )

            score_column, route_column = st.columns([1, 3])

            with score_column:
                st.metric("路线评分", f"{quality_score_result['score']} / 100")
                st.progress(quality_score_result["score"] / 100)

            with route_column:
                route_text = " → ".join(place["name"] for place in day_plan["places"])
                st.info(f"当天路线：{route_text}")

            with st.expander("查看评分依据"):
                st.markdown("**优点**")
                for advantage in quality_score_result["advantages"]:
                    st.write(f"- {advantage}")

                st.markdown("**风险**")
                for risk in quality_score_result["risks"]:
                    st.write(f"- {risk}")

            day_quality_notes = build_day_quality_notes(day_plan)

            for note in day_quality_notes:
                st.warning(note)

            for section_name in BEST_TIME_OPTIONS:
                section_places = [
                    place
                    for place in day_plan["places"]
                    if place["best_time"] == section_name
                ]

                if not section_places:
                    continue

                st.markdown(f"### {section_name}")

                for place in section_places:
                    with st.container():
                        st.markdown(f"**{place['name']}**")
                        st.write(place["description"])
                        st.caption(
                            f"类型：{place['place_type']}｜"
                            f"区域：{place['area']}｜"
                            f"建议停留：{place['duration_minutes']} 分钟｜"
                            f"推荐时间：{place['best_time']}"
                        )
                        st.link_button(
                            f"打开高德地图搜索：{place['name']}",
                            place["amap_url"],
                        )

    copy_text = build_trip_markdown(
        selected_city=selected_city,
        travel_days=travel_days,
        travel_pace=travel_pace,
        selected_trip_style=selected_trip_style,
        generation_mode=generation_mode,
        weather_mode=weather_mode,
        route_version=route_version,
        selected_preferences=selected_preferences,
        selected_travel_scope=selected_travel_scope,
        required_place_names=required_place_names,
        excluded_place_names=excluded_place_names,
        trip_plan=trip_plan,
    )

    st.subheader("可复制路线")
    st.text_area(
        "复制下面的内容，可以发到微信、备忘录或小红书草稿",
        copy_text,
        height=300,
    )

    download_file_name = build_trip_file_name(
        selected_city,
        travel_days,
        travel_pace,
        selected_trip_style,
    )

    st.download_button(
        "下载 Markdown 路线文件",
        data=copy_text,
        file_name=download_file_name,
        mime="text/markdown",
        use_container_width=True,
    )

else:
    st.info("请先在左侧选择路线条件，然后点击“生成路线”。")