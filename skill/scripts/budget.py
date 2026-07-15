"""
AI 旅行规划师 - 预算计算与分配模块
=====================================
根据目的地消费水平、出行天数、人数等因素，
智能分配住宿/餐饮/交通/门票/购物预算。

使用方式:
    python budget.py --destination 成都 --days 4 --budget 5000 --travelers 2
"""

import json
import os
import argparse
from typing import Dict, List
from dataclasses import dataclass, field

# ============================================================
# 数据结构
# ============================================================

@dataclass
class BudgetBreakdown:
    """预算分解"""
    accommodation: float = 0.0    # 住宿
    food: float = 0.0             # 餐饮
    transportation: float = 0.0   # 交通
    tickets: float = 0.0          # 门票
    shopping: float = 0.0         # 购物/其他
    total: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "住宿": self.accommodation,
            "餐饮": self.food,
            "交通": self.transportation,
            "门票": self.tickets,
            "购物/其他": self.shopping,
            "总计": self.total
        }

# ============================================================
# 预算模板加载
# ============================================================

def load_budget_templates() -> Dict:
    """加载预算模板"""
    path = os.path.join(
        os.path.dirname(__file__), "..", "references", "budget_templates.json"
    )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ============================================================
# 预算分配算法
# ============================================================

# 不同住宿等级的每日价格范围(元)
ACCOMMODATION_PRICES = {
    "budget": (100, 200),      # 经济型
    "standard": (250, 450),    # 中等
    "premium": (600, 1200),    # 高档
    "luxury": (1500, 3000)     # 豪华
}

# 预算分配比例(根据总预算级别)
BUDGET_RATIOS = {
    "tight": {          # 紧凑型(人均<500/天)
        "accommodation": 0.35,
        "food": 0.25,
        "transportation": 0.15,
        "tickets": 0.15,
        "shopping": 0.10
    },
    "comfortable": {    # 舒适型(人均500-1000/天)
        "accommodation": 0.30,
        "food": 0.25,
        "transportation": 0.15,
        "tickets": 0.15,
        "shopping": 0.15
    },
    "luxury": {         # 豪华型(人均>1000/天)
        "accommodation": 0.35,
        "food": 0.20,
        "transportation": 0.15,
        "tickets": 0.10,
        "shopping": 0.20
    }
}

def determine_budget_level(per_person_daily: float) -> str:
    """根据人均日预算确定预算级别"""
    if per_person_daily < 500:
        return "tight"
    elif per_person_daily < 1000:
        return "comfortable"
    else:
        return "luxury"

def calculate_budget(
    destination: str,
    days: int,
    total_budget: float,
    travelers: int = 1,
    accommodation_level: str = "standard"
) -> BudgetBreakdown:
    """
    计算预算分配方案。

    参数:
        destination: 目的地城市
        days: 天数
        total_budget: 总预算(元)
        travelers: 人数
        accommodation_level: 住宿等级
    """
    # 加载目的地消费系数
    templates = load_budget_templates()
    city_coefficient = templates.get("city_coefficients", {}).get(destination, 1.0)

    # 计算人均日预算
    per_person_daily = total_budget / travelers / days
    budget_level = determine_budget_level(per_person_daily)
    ratios = BUDGET_RATIOS[budget_level]

    # 基础分配
    breakdown = BudgetBreakdown(
        accommodation=total_budget * ratios["accommodation"],
        food=total_budget * ratios["food"],
        transportation=total_budget * ratios["transportation"],
        tickets=total_budget * ratios["tickets"],
        shopping=total_budget * ratios["shopping"],
        total=total_budget
    )

    # 根据城市消费水平调整
    # 一线城市消费高，住宿和餐饮上浮
    if city_coefficient > 1.2:
        breakdown.accommodation *= 1.1
        breakdown.food *= 1.1
        breakdown.shopping *= 0.9  # 购物预算相对降低

    # 住宿等级调整
    price_range = ACCOMMODATION_PRICES.get(accommodation_level, ACCOMMODATION_PRICES["standard"])
    expected_accommodation = price_range[0] * city_coefficient * days
    if breakdown.accommodation < expected_accommodation:
        # 住宿预算不足，从购物预算调配
        deficit = expected_accommodation - breakdown.accommodation
        transfer = min(deficit, breakdown.shopping * 0.5)
        breakdown.accommodation += transfer
        breakdown.shopping -= transfer

    return breakdown

def optimize_budget(
    breakdown: BudgetBreakdown,
    constraints: Dict = None
) -> BudgetBreakdown:
    """
    优化预算分配。
    根据用户约束(如最低住宿标准、最大餐饮支出等)调整分配。
    """
    if not constraints:
        return breakdown

    # 调整逻辑
    if "min_accommodation" in constraints:
        min_acc = constraints["min_accommodation"]
        if breakdown.accommodation < min_acc:
            deficit = min_acc - breakdown.accommodation
            # 从购物和其他中调配
            from_shopping = min(deficit * 0.6, breakdown.shopping)
            from_tickets = min(deficit * 0.4, breakdown.tickets * 0.3)
            breakdown.accommodation += from_shopping + from_tickets
            breakdown.shopping -= from_shopping
            breakdown.tickets -= from_tickets

    if "max_food" in constraints:
        if breakdown.food > constraints["max_food"]:
            excess = breakdown.food - constraints["max_food"]
            breakdown.food = constraints["max_food"]
            breakdown.shopping += excess

    return breakdown

def generate_budget_report(breakdown: BudgetBreakdown, days: int, travelers: int) -> str:
    """生成预算报告"""
    report = []
    report.append("=" * 50)
    report.append("       AI 旅行规划师 - 预算分配方案")
    report.append("=" * 50)
    report.append(f"  出行天数: {days}天 | 人数: {travelers}人")
    report.append(f"  总预算: ¥{breakdown.total:.2f}")
    report.append("-" * 50)
    report.append(f"  住宿:     ¥{breakdown.accommodation:>10.2f}  ({breakdown.accommodation/breakdown.total*100:.1f}%)")
    report.append(f"  餐饮:     ¥{breakdown.food:>10.2f}  ({breakdown.food/breakdown.total*100:.1f}%)")
    report.append(f"  交通:     ¥{breakdown.transportation:>10.2f}  ({breakdown.transportation/breakdown.total*100:.1f}%)")
    report.append(f"  门票:     ¥{breakdown.tickets:>10.2f}  ({breakdown.tickets/breakdown.total*100:.1f}%)")
    report.append(f"  购物/其他: ¥{breakdown.shopping:>9.2f}  ({breakdown.shopping/breakdown.total*100:.1f}%)")
    report.append("-" * 50)
    report.append(f"  人均日预算: ¥{breakdown.total/travelers/days:.2f}/人/天")
    report.append("=" * 50)

    # 建议部分
    report.append("\n  💡 预算建议:")
    per_person_daily = breakdown.total / travelers / days
    if per_person_daily < 300:
        report.append("  - 预算较紧，建议选择青旅/民宿，多体验免费景点")
    elif per_person_daily < 800:
        report.append("  - 预算适中，可选择经济连锁酒店，合理搭配收费/免费景点")
    else:
        report.append("  - 预算充裕，可提升住宿品质，体验特色餐饮和活动")

    return "\n".join(report)

# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AI 旅行规划师 - 预算计算")
    parser.add_argument("--destination", "-d", required=True, help="目的地城市")
    parser.add_argument("--days", type=int, required=True, help="出行天数")
    parser.add_argument("--budget", type=float, required=True, help="总预算(元)")
    parser.add_argument("--travelers", type=int, default=1, help="出行人数")
    parser.add_argument("--level", default="standard",
                        choices=["budget", "standard", "premium", "luxury"],
                        help="住宿等级")

    args = parser.parse_args()

    breakdown = calculate_budget(
        destination=args.destination,
        days=args.days,
        total_budget=args.budget,
        travelers=args.travelers,
        accommodation_level=args.level
    )

    report = generate_budget_report(breakdown, args.days, args.travelers)
    print(report)

if __name__ == "__main__":
    main()
