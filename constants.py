# ./constants.py

TRAVEL_PACE_OPTIONS = (
    "轻松",
    "标准",
    "特种兵",
)

PLACES_PER_DAY_BY_PACE = {
    "轻松": 3,
    "标准": 4,
    "特种兵": 5,
}

PACE_DURATION_RANGES = {
    "轻松": (180, 360),
    "标准": (300, 480),
    "特种兵": (420, 600),
}

TRIP_STYLE_OPTIONS = (
    "经典优先",
    "美食优先",
    "拍照优先",
    "亲子轻松",
    "自然风景",
    "小众慢游",
)

TRIP_STYLE_TAG_WEIGHTS = {
    "经典优先": {
        "经典景点": 5,
        "历史文化": 2,
        "夜景": 1,
    },
    "美食优先": {
        "美食": 5,
        "购物": 2,
        "夜景": 1,
    },
    "拍照优先": {
        "拍照": 5,
        "夜景": 2,
        "自然风景": 2,
    },
    "亲子轻松": {
        "亲子": 5,
        "轻松": 4,
        "室内": 2,
        "自然风景": 1,
    },
    "自然风景": {
        "自然风景": 5,
        "轻松": 2,
        "拍照": 1,
    },
    "小众慢游": {
        "轻松": 4,
        "历史文化": 2,
        "自然风景": 2,
        "拍照": 1,
    },
}

GENERATION_MODE_OPTIONS = (
    "稳定推荐",
    "轻微变化",
    "随机探索",
)

VARIATION_STRENGTH_BY_MODE = {
    "稳定推荐": 0,
    "轻微变化": 3,
    "随机探索": 7,
}

WEATHER_MODE_OPTIONS = (
    "正常天气",
    "下雨",
    "炎热",
)

BEST_TIME_OPTIONS = (
    "上午",
    "下午",
    "晚上",
)

TIME_ORDER = {
    "上午": 1,
    "下午": 2,
    "晚上": 3,
}

TRAVEL_SCOPE_ALL = "不限"
TRAVEL_SCOPE_CITY_ONLY = "只玩市区"
TRAVEL_SCOPE_CITY_AND_AROUND = "市区 + 周边"
TRAVEL_SCOPE_FAR_NATURE = "远郊 / 自然优先"

TRAVEL_SCOPE_OPTIONS = (
    TRAVEL_SCOPE_ALL,
    TRAVEL_SCOPE_CITY_ONLY,
    TRAVEL_SCOPE_CITY_AND_AROUND,
    TRAVEL_SCOPE_FAR_NATURE,
)

DATA_TRAVEL_SCOPE_CITY = "市区"
DATA_TRAVEL_SCOPE_AROUND = "周边"
DATA_TRAVEL_SCOPE_FAR = "远郊"

DATA_TRAVEL_SCOPE_OPTIONS = (
    DATA_TRAVEL_SCOPE_CITY,
    DATA_TRAVEL_SCOPE_AROUND,
    DATA_TRAVEL_SCOPE_FAR,
)

CSV_TRAVEL_SCOPE_OPTIONS = (
    DATA_TRAVEL_SCOPE_CITY,
    DATA_TRAVEL_SCOPE_AROUND,
    DATA_TRAVEL_SCOPE_FAR,
    "",
)

SCOPE_FILTER_MAP = {
    TRAVEL_SCOPE_CITY_ONLY: {
        DATA_TRAVEL_SCOPE_CITY,
    },
    TRAVEL_SCOPE_CITY_AND_AROUND: {
        DATA_TRAVEL_SCOPE_CITY,
        DATA_TRAVEL_SCOPE_AROUND,
    },
    TRAVEL_SCOPE_FAR_NATURE: {
        DATA_TRAVEL_SCOPE_FAR,
        DATA_TRAVEL_SCOPE_AROUND,
    },
}

SUPPORTED_TAGS = (
    "自然风景",
    "历史文化",
    "经典景点",
    "美食",
    "购物",
    "夜景",
    "拍照",
    "轻松",
    "亲子",
    "寺庙",
    "室内",
    "红色文化",
    "演出",
)

PLACE_TYPE_OPTIONS = (
    "景点",
    "自然",
    "文化",
    "美食",
    "购物",
    "夜游",
    "亲子",
    "交通",
)

DEFAULT_PREFERENCE_OPTIONS = (
    "自然风景",
    "历史文化",
    "经典景点",
    "美食",
    "购物",
    "夜景",
    "拍照",
    "轻松",
    "亲子",
    "寺庙",
    "室内",
)

DEFAULT_SELECTED_PREFERENCES = (
    "自然风景",
    "美食",
    "轻松",
)

REQUIRED_CSV_FIELD_NAMES = {
    "city",
    "name",
    "place_type",
    "area",
    "route_group",
    "route_order",
    "tags",
    "best_time",
    "duration_minutes",
    "score",
    "description",
}

REQUIRED_JSON_PLACE_FIELD_NAMES = {
    "name",
    "place_type",
    "area",
    "route_group",
    "route_order",
    "tags",
    "best_time",
    "duration_minutes",
    "score",
    "description",
}