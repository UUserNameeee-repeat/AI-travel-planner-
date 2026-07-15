"""
AI 旅行规划师 - 天气查询模块
=====================================
查询目的地天气信息，为行程规划提供天气参考。
支持离线模式（使用季节性气候模板）和在线模式。

使用方式:
    python weather.py --city 成都 --date 2025-10-01
"""

import json
import os
import argparse
from datetime import datetime, timedelta
from typing import Dict, Optional, List

# ============================================================
# 季节性气候模板（离线模式使用）
# ============================================================

# 各城市各月份平均气候数据
# 数据格式: { 月份: { "temp_range": [最低, 最高], "weather": "天气描述", "rain_prob": 降水概率 } }
CLIMATE_TEMPLATES = {
    "成都": {
        1: {"temp_range": [2, 9], "weather": "多云", "rain_prob": 0.15},
        2: {"temp_range": [4, 11], "weather": "多云", "rain_prob": 0.20},
        3: {"temp_range": [8, 16], "weather": "阴", "rain_prob": 0.30},
        4: {"temp_range": [13, 22], "weather": "阵雨", "rain_prob": 0.40},
        5: {"temp_range": [17, 26], "weather": "阵雨", "rain_prob": 0.45},
        6: {"temp_range": [20, 28], "weather": "雨", "rain_prob": 0.55},
        7: {"temp_range": [22, 30], "weather": "雨", "rain_prob": 0.60},
        8: {"temp_range": [22, 30], "weather": "阵雨", "rain_prob": 0.55},
        9: {"temp_range": [18, 25], "weather": "阵雨", "rain_prob": 0.45},
        10: {"temp_range": [13, 20], "weather": "阴", "rain_prob": 0.35},
        11: {"temp_range": [8, 15], "weather": "多云", "rain_prob": 0.20},
        12: {"temp_range": [3, 10], "weather": "多云", "rain_prob": 0.15},
    },
    "北京": {
        1: {"temp_range": [-9, 2], "weather": "晴", "rain_prob": 0.05},
        2: {"temp_range": [-6, 5], "weather": "晴", "rain_prob": 0.10},
        3: {"temp_range": [0, 12], "weather": "晴", "rain_prob": 0.15},
        4: {"temp_range": [7, 20], "weather": "晴", "rain_prob": 0.15},
        5: {"temp_range": [13, 26], "weather": "晴", "rain_prob": 0.20},
        6: {"temp_range": [18, 30], "weather": "雷阵雨", "rain_prob": 0.35},
        7: {"temp_range": [22, 31], "weather": "雷阵雨", "rain_prob": 0.45},
        8: {"temp_range": [21, 30], "weather": "雷阵雨", "rain_prob": 0.40},
        9: {"temp_range": [15, 26], "weather": "晴", "rain_prob": 0.20},
        10: {"temp_range": [7, 18], "weather": "晴", "rain_prob": 0.10},
        11: {"temp_range": [-1, 9], "weather": "晴", "rain_prob": 0.08},
        12: {"temp_range": [-7, 3], "weather": "晴", "rain_prob": 0.05},
    },
    "上海": {
        1: {"temp_range": [1, 8], "weather": "阴", "rain_prob": 0.30},
        2: {"temp_range": [2, 9], "weather": "阴", "rain_prob": 0.35},
        3: {"temp_range": [6, 13], "weather": "阵雨", "rain_prob": 0.40},
        4: {"temp_range": [11, 19], "weather": "阵雨", "rain_prob": 0.45},
        5: {"temp_range": [16, 24], "weather": "阵雨", "rain_prob": 0.45},
        6: {"temp_range": [20, 27], "weather": "雨", "rain_prob": 0.55},
        7: {"temp_range": [24, 32], "weather": "晴", "rain_prob": 0.35},
        8: {"temp_range": [24, 32], "weather": "晴", "rain_prob": 0.35},
        9: {"temp_range": [20, 27], "weather": "阵雨", "rain_prob": 0.40},
        10: {"temp_range": [14, 22], "weather": "阴", "rain_prob": 0.25},
        11: {"temp_range": [8, 16], "weather": "阴", "rain_prob": 0.25},
        12: {"temp_range": [2, 10], "weather": "阴", "rain_prob": 0.25},
    },
    "西安": {
        1: {"temp_range": [-5, 4], "weather": "晴", "rain_prob": 0.10},
        2: {"temp_range": [-2, 8], "weather": "多云", "rain_prob": 0.15},
        3: {"temp_range": [3, 14], "weather": "多云", "rain_prob": 0.25},
        4: {"temp_range": [9, 21], "weather": "阵雨", "rain_prob": 0.30},
        5: {"temp_range": [14, 26], "weather": "晴", "rain_prob": 0.25},
        6: {"temp_range": [19, 31], "weather": "雷阵雨", "rain_prob": 0.35},
        7: {"temp_range": [22, 34], "weather": "晴", "rain_prob": 0.30},
        8: {"temp_range": [21, 32], "weather": "阵雨", "rain_prob": 0.35},
        9: {"temp_range": [15, 25], "weather": "阵雨", "rain_prob": 0.35},
        10: {"temp_range": [9, 18], "weather": "多云", "rain_prob": 0.25},
        11: {"temp_range": [2, 11], "weather": "晴", "rain_prob": 0.15},
        12: {"temp_range": [-4, 5], "weather": "晴", "rain_prob": 0.10},
    },
    "杭州": {
        1: {"temp_range": [1, 8], "weather": "阴", "rain_prob": 0.35},
        2: {"temp_range": [2, 10], "weather": "阴", "rain_prob": 0.38},
        3: {"temp_range": [6, 14], "weather": "阵雨", "rain_prob": 0.42},
        4: {"temp_range": [12, 20], "weather": "阵雨", "rain_prob": 0.45},
        5: {"temp_range": [17, 25], "weather": "阵雨", "rain_prob": 0.45},
        6: {"temp_range": [21, 28], "weather": "雨", "rain_prob": 0.55},
        7: {"temp_range": [25, 33], "weather": "晴", "rain_prob": 0.30},
        8: {"temp_range": [25, 33], "weather": "晴", "rain_prob": 0.30},
        9: {"temp_range": [20, 27], "weather": "阵雨", "rain_prob": 0.40},
        10: {"temp_range": [14, 22], "weather": "多云", "rain_prob": 0.25},
        11: {"temp_range": [8, 16], "weather": "阴", "rain_prob": 0.25},
        12: {"temp_range": [2, 10], "weather": "阴", "rain_prob": 0.25},
    },
    "default": {
        1: {"temp_range": [0, 10], "weather": "多云", "rain_prob": 0.25},
        2: {"temp_range": [2, 12], "weather": "多云", "rain_prob": 0.25},
        3: {"temp_range": [6, 16], "weather": "多云", "rain_prob": 0.30},
        4: {"temp_range": [12, 22], "weather": "阵雨", "rain_prob": 0.35},
        5: {"temp_range": [17, 27], "weather": "晴", "rain_prob": 0.30},
        6: {"temp_range": [21, 30], "weather": "阵雨", "rain_prob": 0.40},
        7: {"temp_range": [24, 33], "weather": "晴", "rain_prob": 0.30},
        8: {"temp_range": [23, 32], "weather": "晴", "rain_prob": 0.30},
        9: {"temp_range": [18, 27], "weather": "多云", "rain_prob": 0.30},
        10: {"temp_range": [12, 21], "weather": "多云", "rain_prob": 0.25},
        11: {"temp_range": [6, 15], "weather": "多云", "rain_prob": 0.20},
        12: {"temp_range": [1, 9], "weather": "多云", "rain_prob": 0.20},
    }
}

# ============================================================
# 天气查询
# ============================================================

def get_weather(city: str, date: str = None) -> Dict:
    """
    查询城市天气（离线模式，使用季节性气候模板）。

    参数:
        city: 城市名
        date: 日期 YYYY-MM-DD，默认今天

    返回:
        天气信息字典
    """
    if date:
        dt = datetime.strptime(date, "%Y-%m-%d")
    else:
        dt = datetime.now()

    month = dt.month

    # 获取城市气候数据
    city_data = CLIMATE_TEMPLATES.get(city, CLIMATE_TEMPLATES["default"])
    month_data = city_data.get(month, city_data.get(month, CLIMATE_TEMPLATES["default"][month]))

    weather = {
        "city": city,
        "date": dt.strftime("%Y-%m-%d"),
        "temp_min": month_data["temp_range"][0],
        "temp_max": month_data["temp_range"][1],
        "weather": month_data["weather"],
        "rain_probability": month_data["rain_prob"],
        "season": get_season(month),
        "tips": generate_weather_tips(month_data, month)
    }

    return weather

def get_season(month: int) -> str:
    """获取季节"""
    if month in [3, 4, 5]:
        return "春季"
    elif month in [6, 7, 8]:
        return "夏季"
    elif month in [9, 10, 11]:
        return "秋季"
    else:
        return "冬季"

def generate_weather_tips(month_data: Dict, month: int) -> List[str]:
    """根据天气生成出行提示"""
    tips = []
    temp_min = month_data["temp_range"][0]
    temp_max = month_data["temp_range"][1]
    rain_prob = month_data["rain_prob"]

    # 温度提示
    if temp_max > 30:
        tips.append("气温较高，注意防晒补水，避免中午户外活动")
    elif temp_max > 25:
        tips.append("天气温暖，适合户外活动，建议携带防晒霜")
    elif temp_min < 5:
        tips.append("气温较低，注意保暖，建议穿羽绒服或厚外套")
    elif temp_min < 10:
        tips.append("天气偏凉，建议穿外套或毛衣")

    # 降水提示
    if rain_prob > 0.5:
        tips.append("降水概率较高，请携带雨具")
    elif rain_prob > 0.3:
        tips.append("可能有雨，建议携带折叠伞")

    # 季节提示
    if month in [6, 7, 8]:
        tips.append("夏季出行注意防暑，建议携带清凉油")
    elif month in [12, 1, 2]:
        tips.append("冬季出行注意防寒，建议携带暖宝宝")

    return tips

def get_multi_day_weather(city: str, start_date: str, days: int) -> List[Dict]:
    """获取多日天气"""
    weather_list = []
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")

    for i in range(days):
        date = (start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
        weather = get_weather(city, date)
        weather_list.append(weather)

    return weather_list

# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AI 旅行规划师 - 天气查询")
    parser.add_argument("--city", "-c", required=True, help="城市名")
    parser.add_argument("--date", "-d", default=None, help="日期 YYYY-MM-DD")
    parser.add_argument("--days", type=int, default=1, help="查询天数")

    args = parser.parse_args()

    if args.days > 1 and args.date:
        weather_list = get_multi_day_weather(args.city, args.date, args.days)
        for w in weather_list:
            print(f"\n{w['city']} {w['date']} ({w['season']})")
            print(f"  温度: {w['temp_min']}°C ~ {w['temp_max']}°C")
            print(f"  天气: {w['weather']}")
            print(f"  降水概率: {w['rain_probability']*100:.0f}%")
            if w['tips']:
                print(f"  提示:")
                for tip in w['tips']:
                    print(f"    - {tip}")
    else:
        w = get_weather(args.city, args.date)
        print(f"\n{w['city']} {w['date']} ({w['season']})")
        print(f"  温度: {w['temp_min']}°C ~ {w['temp_max']}°C")
        print(f"  天气: {w['weather']}")
        print(f"  降水概率: {w['rain_probability']*100:.0f}%")
        if w['tips']:
            print(f"  提示:")
            for tip in w['tips']:
                print(f"    - {tip}")

if __name__ == "__main__":
    main()
