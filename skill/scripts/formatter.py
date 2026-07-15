"""
AI 旅行规划师 - 输出格式化模块
=====================================
将行程规划结果格式化为多种输出格式(JSON/Markdown/Text)。

使用方式:
    python formatter.py --input plan.json --format markdown
"""

import json
import os
import argparse
from datetime import datetime
from typing import Dict, List
from dataclasses import asdict

# ============================================================
# 格式化器
# ============================================================

def format_as_markdown(plan_data: Dict) -> str:
    """将行程格式化为 Markdown"""
    lines = []

    # 标题
    lines.append(f"# {plan_data['destination']} {plan_data['days']}日游行程规划\n")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # 概览
    lines.append("## 行程概览\n")
    lines.append(f"- **目的地**: {plan_data['destination']}")
    lines.append(f"- **天数**: {plan_data['days']}天")
    lines.append(f"- **出发日期**: {plan_data['start_date']}")
    if plan_data.get('summary'):
        lines.append(f"\n{plan_data['summary']}")
    lines.append("")

    # 每日行程
    for day_plan in plan_data.get('daily_plans', []):
        lines.append(f"## Day {day_plan['day']} - {day_plan['date']} ({day_plan['district']})\n")

        # 上午
        if day_plan.get('morning'):
            lines.append("### 🌅 上午\n")
            for act in day_plan['morning']:
                lines.append(f"- **{act['name']}** ({act['category']})")
                lines.append(f"  - 游玩时长: {act['play_time']}小时")
                lines.append(f"  - 门票: ¥{act['ticket_price']}")
                lines.append(f"  - 评分: {'⭐' * int(act['rating'])}")
                if act.get('description'):
                    lines.append(f"  - 介绍: {act['description']}")
                if act.get('tips'):
                    lines.append(f"  - 💡 提示: {act['tips']}")
                lines.append("")

        # 下午
        if day_plan.get('afternoon'):
            lines.append("### ☀️ 下午\n")
            for act in day_plan['afternoon']:
                lines.append(f"- **{act['name']}** ({act['category']})")
                lines.append(f"  - 游玩时长: {act['play_time']}小时")
                lines.append(f"  - 门票: ¥{act['ticket_price']}")
                lines.append(f"  - 评分: {'⭐' * int(act['rating'])}")
                if act.get('description'):
                    lines.append(f"  - 介绍: {act['description']}")
                lines.append("")

        # 晚上
        if day_plan.get('evening'):
            lines.append("### 🌙 晚上\n")
            for act in day_plan['evening']:
                lines.append(f"- **{act['name']}** ({act['category']})")
                lines.append(f"  - 游玩时长: {act['play_time']}小时")
                lines.append(f"  - 门票: ¥{act['ticket_price']}")
                lines.append("")

        # 餐饮
        if day_plan.get('meals'):
            meals = day_plan['meals']
            lines.append("### 🍽️ 餐饮推荐\n")
            lines.append(f"- 早餐: {meals.get('breakfast', '当地特色')}")
            lines.append(f"- 午餐: {meals.get('lunch', '附近餐厅')}")
            lines.append(f"- 晚餐: {meals.get('dinner', '特色餐厅')}")
            if meals.get('notes'):
                lines.append(f"- 特色: {meals['notes']}")
            lines.append("")

        # 当日统计
        lines.append(f"> 当日游玩: {day_plan['total_time']}h | 花费: ¥{day_plan['total_cost']:.0f}\n")

    # 总预算
    lines.append("## 💰 预算汇总\n")
    lines.append(f"- **总预算估算**: ¥{plan_data.get('total_budget', 0):.0f}")
    lines.append("")

    # 实用提示
    lines.append("## 📌 实用提示\n")
    lines.append("- 请提前预订热门景点门票")
    lines.append("- 关注当地天气预报，合理安排户外活动")
    lines.append("- 建议下载离线地图，以防网络不佳")
    lines.append("- 贵重物品随身携带，注意安全")
    lines.append("- 尊重当地文化习俗")
    lines.append("")

    return "\n".join(lines)

def format_as_text(plan_data: Dict) -> str:
    """将行程格式化为纯文本"""
    lines = []
    sep = "=" * 50

    lines.append(sep)
    lines.append(f"  {plan_data['destination']} {plan_data['days']}日游行程")
    lines.append(sep)
    lines.append(f"  出发日期: {plan_data['start_date']}")
    lines.append("")

    for day_plan in plan_data.get('daily_plans', []):
        lines.append("-" * 50)
        lines.append(f"  Day {day_plan['day']} | {day_plan['date']} | {day_plan['district']}")
        lines.append("-" * 50)

        if day_plan.get('morning'):
            lines.append("\n  [上午]")
            for act in day_plan['morning']:
                lines.append(f"    {act['name']} - {act['play_time']}h - ¥{act['ticket_price']}")

        if day_plan.get('afternoon'):
            lines.append("\n  [下午]")
            for act in day_plan['afternoon']:
                lines.append(f"    {act['name']} - {act['play_time']}h - ¥{act['ticket_price']}")

        if day_plan.get('evening'):
            lines.append("\n  [晚上]")
            for act in day_plan['evening']:
                lines.append(f"    {act['name']} - {act['play_time']}h - ¥{act['ticket_price']}")

        if day_plan.get('meals'):
            m = day_plan['meals']
            lines.append(f"\n  [餐饮] 早:{m.get('breakfast','')} 午:{m.get('lunch','')} 晚:{m.get('dinner','')}")

        lines.append(f"\n  小计: {day_plan['total_time']}h | ¥{day_plan['total_cost']:.0f}\n")

    lines.append(sep)
    lines.append(f"  总预算: ¥{plan_data.get('total_budget', 0):.0f}")
    lines.append(sep)

    return "\n".join(lines)

def format_as_json(plan_data: Dict) -> str:
    """将行程格式化为 JSON"""
    return json.dumps(plan_data, ensure_ascii=False, indent=2)

def save_plan(plan_data: Dict, output_path: str, fmt: str = "markdown"):
    """保存行程到文件"""
    if fmt == "markdown":
        content = format_as_markdown(plan_data)
    elif fmt == "text":
        content = format_as_text(plan_data)
    elif fmt == "json":
        content = format_as_json(plan_data)
    else:
        raise ValueError(f"不支持的格式: {fmt}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path

# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AI 旅行规划师 - 格式化输出")
    parser.add_argument("--input", "-i", required=True, help="行程JSON文件路径")
    parser.add_argument("--format", "-f", default="markdown",
                        choices=["markdown", "text", "json"],
                        help="输出格式")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    if args.format == "markdown":
        result = format_as_markdown(plan_data)
    elif args.format == "text":
        result = format_as_text(plan_data)
    else:
        result = format_as_json(plan_data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"已保存到: {args.output}")
    else:
        print(result)

if __name__ == "__main__":
    main()
