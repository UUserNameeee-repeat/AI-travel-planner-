"""
AI 旅行规划师 - 核心行程规划引擎
=====================================
根据用户需求，智能编排每日行程。

核心算法：
1. 根据偏好从景点池中筛选候选景点
2. 按地理位置聚类，减少跨区移动
3. 根据游玩时长和开放时间编排每日行程
4. 平衡每日游玩强度，避免过载

使用方式:
    python planner.py --destination 成都 --days 4 --preferences food,nature
"""

import json
import os
import random
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# ============================================================
# 数据结构定义
# ============================================================

@dataclass
class Attraction:
    """景点信息"""
    name: str
    category: str              # 分类: culture/nature/food/...
    district: str              # 所在区域
    play_time: float           # 建议游玩时间(小时)
    ticket_price: float        # 门票价格(元)
    rating: float              # 评分(1-5)
    tags: List[str] = field(default_factory=list)
    best_time: str = "all_day" # 最佳游玩时段: morning/afternoon/evening/all_day
    description: str = ""
    tips: str = ""

@dataclass
class DayPlan:
    """单日行程"""
    day: int
    date: str
    morning: List[Dict] = field(default_factory=list)     # 上午活动
    afternoon: List[Dict] = field(default_factory=list)   # 下午活动
    evening: List[Dict] = field(default_factory=list)     # 晚上活动
    meals: Dict = field(default_factory=dict)             # 餐饮推荐
    total_cost: float = 0.0
    total_time: float = 0.0
    district: str = ""  # 当日主要活动区域

@dataclass
class TravelPlan:
    """完整旅行计划"""
    destination: str
    days: int
    start_date: str
    daily_plans: List[DayPlan] = field(default_factory=list)
    total_budget: float = 0.0
    summary: str = ""

# ============================================================
# 知识库加载
# ============================================================

def load_destinations_db() -> Dict:
    """加载目的地知识库"""
    db_path = os.path.join(
        os.path.dirname(__file__), "..", "references", "destinations.json"
    )
    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_budget_templates() -> Dict:
    """加载预算模板"""
    db_path = os.path.join(
        os.path.dirname(__file__), "..", "references", "budget_templates.json"
    )
    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ============================================================
# 景点筛选与推荐
# ============================================================

def filter_attractions(
    attractions: List[Dict],
    preferences: List[str],
    max_per_day: int = 4
) -> List[Attraction]:
    """
    根据用户偏好筛选景点，并按匹配度排序。
    """
    scored = []
    for attr_data in attractions:
        attr = Attraction(
            name=attr_data["name"],
            category=attr_data["category"],
            district=attr_data["district"],
            play_time=attr_data["play_time"],
            ticket_price=attr_data.get("ticket_price", 0),
            rating=attr_data.get("rating", 4.0),
            tags=attr_data.get("tags", []),
            best_time=attr_data.get("best_time", "all_day"),
            description=attr_data.get("description", ""),
            tips=attr_data.get("tips", "")
        )

        # 计算匹配分数
        score = attr.rating * 2  # 基础分: 评分权重

        # 偏好匹配加分
        if attr.category in preferences:
            score += 5
        for tag in attr.tags:
            if tag in preferences:
                score += 2

        scored.append((attr, score))

    # 按分数降序排列
    scored.sort(key=lambda x: x[1], reverse=True)

    # 返回前 N 个景点
    return [item[0] for item in scored[:max_per_day * 3]]  # 候选池放大

# ============================================================
# 行程编排核心算法
# ============================================================

def cluster_by_district(attractions: List[Attraction]) -> Dict[str, List[Attraction]]:
    """按区域聚类景点，减少跨区移动"""
    clusters = {}
    for attr in attractions:
        if attr.district not in clusters:
            clusters[attr.district] = []
        clusters[attr.district].append(attr)
    return clusters

def assign_time_slot(attraction: Attraction) -> str:
    """根据景点最佳游玩时段分配时间段"""
    if attraction.best_time == "morning":
        return "morning"
    elif attraction.best_time == "afternoon":
        return "afternoon"
    elif attraction.best_time == "evening":
        return "evening"
    else:
        # all_day: 根据游玩时长分配
        if attraction.play_time <= 2:
            return "morning"
        elif attraction.play_time <= 3:
            return "afternoon"
        else:
            return "morning"  # 大景点放上午

def plan_single_day(
    day: int,
    date: str,
    district: str,
    attractions: List[Attraction],
    max_hours: float = 8.0
) -> DayPlan:
    """
    编排单日行程。
    策略: 按时段填充，控制总游玩时间不超过 max_hours。
    对于 all_day 景点，可以放入任意时段。
    大景点(>3h)可以跨时段，放入最合适的时段即可。
    """
    plan = DayPlan(day=day, date=date, district=district)
    used_time = 0.0
    used_names = set()

    # 按时段填充 — 放宽单时段上限以支持大景点
    slots = ["morning", "afternoon", "evening"]
    slot_limits = {"morning": 5.0, "afternoon": 5.0, "evening": 3.0}
    slot_used = {"morning": 0.0, "afternoon": 0.0, "evening": 0.0}

    # 第一轮: 先安排有固定时段要求的景点
    for slot in slots:
        for attr in attractions:
            if attr.name in used_names:
                continue
            if attr.best_time == "all_day":
                continue  # 跳过全天景点，第二轮处理
            if slot_used[slot] + attr.play_time > slot_limits[slot]:
                continue
            if used_time + attr.play_time > max_hours:
                continue

            if attr.best_time != slot:
                continue

            activity = {
                "name": attr.name,
                "category": attr.category,
                "play_time": attr.play_time,
                "ticket_price": attr.ticket_price,
                "rating": attr.rating,
                "description": attr.description,
                "tips": attr.tips
            }

            if slot == "morning":
                plan.morning.append(activity)
            elif slot == "afternoon":
                plan.afternoon.append(activity)
            else:
                plan.evening.append(activity)

            used_time += attr.play_time
            slot_used[slot] += attr.play_time
            used_names.add(attr.name)
            plan.total_cost += attr.ticket_price
            plan.total_time += attr.play_time

    # 第二轮: 安排 all_day 景点到还有余量的时段
    for slot in slots:
        for attr in attractions:
            if attr.name in used_names:
                continue
            if attr.best_time != "all_day":
                continue
            if slot_used[slot] + attr.play_time > slot_limits[slot]:
                continue
            if used_time + attr.play_time > max_hours:
                continue

            activity = {
                "name": attr.name,
                "category": attr.category,
                "play_time": attr.play_time,
                "ticket_price": attr.ticket_price,
                "rating": attr.rating,
                "description": attr.description,
                "tips": attr.tips
            }

            if slot == "morning":
                plan.morning.append(activity)
            elif slot == "afternoon":
                plan.afternoon.append(activity)
            else:
                plan.evening.append(activity)

            used_time += attr.play_time
            slot_used[slot] += attr.play_time
            used_names.add(attr.name)
            plan.total_cost += attr.ticket_price
            plan.total_time += attr.play_time

    return plan

def generate_travel_plan(
    destination: str,
    days: int,
    preferences: List[str],
    start_date: str = None,
    travelers: int = 1
) -> TravelPlan:
    """
    生成完整旅行行程。
    """
    # 加载目的地数据
    db = load_destinations_db()
    if destination not in db:
        raise ValueError(f"暂不支持目的地: {destination}。支持的城市: {list(db.keys())}")

    city_data = db[destination]

    # 设置默认出发日期
    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")

    # 筛选景点
    attractions_data = city_data.get("attractions", [])
    selected = filter_attractions(attractions_data, preferences, max_per_day=4)

    # 按区域聚类
    clusters = cluster_by_district(selected)

    # 按景点数量排序区域（优先安排景点多的区域）
    sorted_districts = sorted(clusters.keys(), key=lambda d: len(clusters[d]), reverse=True)

    # 生成每日行程
    plan = TravelPlan(
        destination=destination,
        days=days,
        start_date=start_date
    )

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")

    # 全局已使用的景点名（避免重复安排）
    global_used_names = set()

    for day_idx in range(days):
        date = (start_dt + timedelta(days=day_idx)).strftime("%Y-%m-%d")
        # 轮流分配区域
        district = sorted_districts[day_idx % len(sorted_districts)]
        district_attrs = clusters[district]

        # 过滤掉已使用的景点
        available_attrs = [a for a in district_attrs if a.name not in global_used_names]

        # 如果当前区域景点不够，从其他区域补充
        if len(available_attrs) < 2:
            for other_district in sorted_districts:
                if other_district == district:
                    continue
                for attr in clusters[other_district]:
                    if attr.name not in global_used_names and attr not in available_attrs:
                        available_attrs.append(attr)
                if len(available_attrs) >= 4:
                    break

        day_plan = plan_single_day(
            day=day_idx + 1,
            date=date,
            district=district,
            attractions=available_attrs
        )

        # 记录已使用的景点
        for act in day_plan.morning + day_plan.afternoon + day_plan.evening:
            global_used_names.add(act["name"])

        # 添加餐饮推荐
        restaurants = city_data.get("restaurants", [])
        if restaurants:
            day_plan.meals = recommend_meals(restaurants, district, preferences)

        plan.daily_plans.append(day_plan)

    # 生成摘要
    plan.summary = generate_summary(plan, city_data)
    plan.total_budget = sum(dp.total_cost for dp in plan.daily_plans) * travelers

    return plan

# ============================================================
# 餐饮推荐
# ============================================================

def recommend_meals(
    restaurants: List[Dict],
    district: str,
    preferences: List[str]
) -> Dict:
    """推荐每日餐饮"""
    # 优先推荐同区域的餐厅
    same_district = [r for r in restaurants if r.get("district") == district]
    other_district = [r for r in restaurants if r.get("district") != district]

    pool = same_district if len(same_district) >= 3 else same_district + other_district

    if not pool:
        return {"breakfast": "当地特色早餐", "lunch": "附近餐厅", "dinner": "特色餐厅"}

    # 按评分排序
    pool.sort(key=lambda r: r.get("rating", 4.0), reverse=True)

    return {
        "breakfast": pool[0]["name"] if len(pool) > 0 else "当地特色早餐",
        "lunch": pool[1]["name"] if len(pool) > 1 else pool[0]["name"],
        "dinner": pool[2]["name"] if len(pool) > 2 else pool[0]["name"],
        "notes": pool[0].get("specialty", "")
    }

# ============================================================
# 摘要生成
# ============================================================

def generate_summary(plan: TravelPlan, city_data: Dict) -> str:
    """生成行程摘要"""
    city_info = city_data.get("city_info", {})
    total_attractions = sum(
        len(dp.morning) + len(dp.afternoon) + len(dp.evening)
        for dp in plan.daily_plans
    )

    summary = (
        f"本次旅行目的地: {plan.destination}\n"
        f"行程天数: {plan.days}天\n"
        f"出发日期: {plan.start_date}\n"
        f"计划游览景点: {total_attractions}个\n"
    )

    if city_info:
        summary += f"城市简介: {city_info.get('description', '')}\n"
        summary += f"最佳季节: {city_info.get('best_season', '')}\n"
        summary += f"当地美食: {city_info.get('local_food', '')}\n"

    # 每日区域安排
    summary += "\n每日区域安排:\n"
    for dp in plan.daily_plans:
        summary += f"  Day {dp.day} ({dp.date}): {dp.district}\n"

    return summary

# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AI 旅行规划师")
    parser.add_argument("--destination", "-d", required=True, help="目的地城市")
    parser.add_argument("--days", type=int, default=3, help="出行天数")
    parser.add_argument("--preferences", "-p", default="food,nature,culture",
                        help="兴趣偏好(逗号分隔)")
    parser.add_argument("--start-date", default=None, help="出发日期 YYYY-MM-DD")
    parser.add_argument("--travelers", type=int, default=1, help="出行人数")

    args = parser.parse_args()

    preferences = [p.strip() for p in args.preferences.split(",")]

    plan = generate_travel_plan(
        destination=args.destination,
        days=args.days,
        preferences=preferences,
        start_date=args.start_date,
        travelers=args.travelers
    )

    # 输出行程
    print("=" * 60)
    print("       AI 旅行规划师 - 行程方案")
    print("=" * 60)
    print(plan.summary)
    print("-" * 60)

    for dp in plan.daily_plans:
        print(f"\n{'='*40}")
        print(f"  Day {dp.day} | {dp.date} | 区域: {dp.district}")
        print(f"{'='*40}")

        if dp.morning:
            print("\n  🌅 上午:")
            for act in dp.morning:
                print(f"     - {act['name']} ({act['category']})")
                print(f"       游玩: {act['play_time']}h | 门票: ¥{act['ticket_price']}")
                if act.get('tips'):
                    print(f"       💡 {act['tips']}")

        if dp.afternoon:
            print("\n  ☀️ 下午:")
            for act in dp.afternoon:
                print(f"     - {act['name']} ({act['category']})")
                print(f"       游玩: {act['play_time']}h | 门票: ¥{act['ticket_price']}")

        if dp.evening:
            print("\n  🌙 晚上:")
            for act in dp.evening:
                print(f"     - {act['name']} ({act['category']})")
                print(f"       游玩: {act['play_time']}h | 门票: ¥{act['ticket_price']}")

        if dp.meals:
            print(f"\n  🍽️ 餐饮推荐:")
            print(f"     早餐: {dp.meals.get('breakfast', '')}")
            print(f"     午餐: {dp.meals.get('lunch', '')}")
            print(f"     晚餐: {dp.meals.get('dinner', '')}")

        print(f"\n  📊 当日统计: 游玩{dp.total_time}h | 花费¥{dp.total_cost:.0f}")

    print(f"\n{'='*60}")
    print(f"  总预算估算: ¥{plan.total_budget:.0f}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
