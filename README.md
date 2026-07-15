# AI 旅行规划师 (AI Travel Planner)

> AI个人系统实践 — 结课作业
>
> 选题：AI旅行规划师

## 选题说明

**AI旅行规划师** 是一个基于 AI 的智能旅行行程规划技能（Skill）。它解决了传统旅行规划中信息分散、决策复杂、耗时长的问题。用户只需提供基本需求（目的地、时间、预算、偏好），即可获得一份包含每日行程、景点推荐、餐饮建议、交通方案、预算明细的完整规划。

### AI 核心价值

本技能的 AI 核心价值体现在：

1. **智能行程编排** —— 根据景点位置、开放时间、游玩时长、用户偏好进行智能排布，避免走回头路
2. **个性化推荐** —— 基于用户兴趣标签进行偏好匹配，推荐最合适的景点和活动
3. **预算智能分配** —— 根据目的地消费水平和用户预算自动分配各项费用比例
4. **上下文感知** —— 考虑天气、季节等因素调整行程建议

## 功能简介

- 🗺️ **智能行程编排**：根据偏好自动筛选景点，按区域聚类编排每日行程
- 💰 **预算智能分配**：根据城市消费水平、出行人数、住宿等级计算最优预算方案
- 🌤️ **天气查询**：提供目的地季节性天气信息和出行提示
- 🍽️ **餐饮推荐**：按区域推荐当地特色餐厅
- 📝 **多格式输出**：支持 Markdown、纯文本、JSON 三种输出格式

## 仓库结构

```
ai-travel-planner/
├── skill/                         # Skill 文件
│   ├── SKILL.md                   # 技能定义文件（含 yaml 前端配置）
│   ├── scripts/                   # 脚本/工具代码
│   │   ├── planner.py             # 核心行程规划引擎
│   │   ├── budget.py              # 预算计算与分配
│   │   ├── formatter.py           # 输出格式化
│   │   └── weather.py             # 天气查询模块
│   └── references/                # 参考文件/配置文件
│       ├── destinations.json      # 目的地知识库（成都/北京/杭州）
│       ├── budget_templates.json  # 预算模板与消费系数
│       └── preferences.json       # 偏好标签映射表
├── data/                          # 测试数据
│   ├── test_cases.json            # 行程规划测试用例
│   ├── sample_output.json         # 示例输出
│   ├── budget_test_data.json      # 预算测试数据
│   └── weather_test_data.json     # 天气测试数据
├── tests/                         # 测试记录
│   └── test_record.md             # 测试环境、步骤、结果记录
├── iteration/                     # 迭代升级说明
│   └── iteration_log.md           # 5个迭代方向详细说明
└── README.md                      # 项目说明
```

## 使用方式

### 1. 行程规划

```bash
python skill/scripts/planner.py \
  --destination 成都 \
  --days 4 \
  --preferences food,nature,culture \
  --start-date 2025-10-01 \
  --travelers 2
```

### 2. 预算计算

```bash
python skill/scripts/budget.py \
  --destination 成都 \
  --days 4 \
  --budget 5000 \
  --travelers 2 \
  --level standard
```

### 3. 天气查询

```bash
python skill/scripts/weather.py \
  --city 成都 \
  --date 2025-10-01 \
  --days 4
```

### 4. 格式化输出

```bash
python skill/scripts/formatter.py \
  --input plan.json \
  --format markdown \
  --output plan.md
```

## 支持的城市

| 城市 | 景点数量 | 餐厅数量 | 特色 |
|------|----------|----------|------|
| 成都 | 12 | 6 | 美食、大熊猫、休闲文化 |
| 北京 | 8 | 4 | 历史古迹、皇家园林 |
| 杭州 | 7 | 4 | 西湖、茶文化、自然风光 |

## 兴趣偏好标签

| 标签 | 说明 |
|------|------|
| `culture` | 历史文化（博物馆、古迹、宗教场所） |
| `nature` | 自然风光（山川、湖泊、公园） |
| `food` | 美食探索（当地特色、街头小吃） |
| `shopping` | 购物（商场、市集、特色店） |
| `adventure` | 冒险户外（徒步、攀岩、水上运动） |
| `nightlife` | 夜生活（酒吧、夜市、演出） |
| `photography` | 摄影打卡（地标、网红点） |
| `relaxation` | 休闲放松（温泉、SPA、咖啡馆） |

## 技术栈

- **语言**: Python 3.10+
- **依赖**: 仅使用 Python 标准库（json, argparse, dataclasses, typing）
- **数据格式**: JSON
- **输出格式**: Markdown / Text / JSON

## 测试结果

所有 8 项测试全部通过 ✅，包括：
- 3 个行程规划测试（成都/北京/杭州）
- 2 个预算计算测试（舒适型/豪华型）
- 2 个天气查询测试（秋季/冬季）
- 1 个错误处理测试

详细测试记录见 `tests/test_record.md`。

## 迭代规划

提供了 5 个后续迭代方向，详见 `iteration/iteration_log.md`：

1. **实时数据接入与在线 API 集成** (P0)
2. **用户画像与个性化推荐引擎** (P1)
3. **多模态输出与可视化行程** (P1)
4. **多目的地路线规划与团队协作** (P2)
5. **智能预算管理与消费追踪** (P2)

## GitHub 仓库

> 请在此处填写你的 GitHub 仓库地址：
>
> `https://github.com/你的用户名/ai-travel-planner`
