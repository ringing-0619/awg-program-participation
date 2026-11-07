# AWG 零售项目参与分析

[English](README.md) | 简体中文

本项目是 **UIUC BADM550 的客户分析项目**，围绕 AWG 零售支持项目开展数据分析与评估。

**Python · pandas · NumPy · statsmodels · Matplotlib · seaborn · Excel**

## 项目概览

- **分析任务：**比较 AIM 自动配货与 One Source 陈列支持各参与组的新品采购和门店覆盖表现，为项目评估提供依据。
- **数据处理：**清洗整合 **54.3万条月度记录**，完成长表转换、标识标准化与多表关联，统一门店 × 商品 × 月份粒度。
- **指标设计：**构建新品上市次月起连续三个月的累计销售额、开票数量及基于采购的门店覆盖率，明确时间窗口与分母。
- **交互回归：**基于 **93,108条门店商品观测**，分别建立“项目 × 品牌”和“项目 × 区域”OLS模型，分析 **5个品牌、9个区域**的细分差异。

## 我的贡献

- **数据处理：**处理 **54万+条原始记录**，完成长表转换、数据清洗、模糊匹配与多表整合，明确**门店 × 商品 × 年月**的基础分析粒度。
- **指标构建 · Checkpoint 1：**围绕不同参与组的新品表现，编写 Python 按**门店 × 上市批次**计算**上市次月起3个月的累计销售额和开票数量**，并计算**商品级门店覆盖率**。
- **回归分析 · Checkpoint 2：**使用 Python 构建**项目 × 品牌 OLS交互回归模型**，通过可视化比较 **5个品牌**在不同参与组的累计销售表现。
- **客户汇报：**制作并讲解两轮汇报中的指标设计、回归方法与品牌分析成果。

## 关键发现

- 第一轮比较中，同时参加两项项目的门店组，**每店平均早期销售额最高**。
- 品牌与区域分析呈现各自的项目表现，形成**品牌定向建议和区域试点优先方向**，并通过两轮客户汇报交付。

![不同品牌与项目参与类别的累计销售对数均值](reports/presentation-excerpts/historical_brand_program_log_sales.png)

## 项目内容

| 内容 | 文件入口 |
|---|---|
| 数据处理与指标计算 | [第一轮 notebook](notebooks/01_checkpoint1_data_and_metrics.ipynb) · [指标定义](docs/methodology.md) |
| 品牌与区域分析 | [第二轮 notebook](notebooks/02_checkpoint2_brand_and_division.ipynb) · [完整成果](docs/checkpoint-2.zh-CN.md) |
| 客户交付物 | [两份完整汇报](presentations/README.md) · [原项目图表](reports/presentation-excerpts/README.md) |

客户工作簿保存在本地，环境配置与输入要求见[运行说明](docs/reproducibility.md)。

[完整案例](docs/case-study.md) · [项目交付](docs/project-deliverables.md) · [原始代码归档](notebooks/archive/README.md) · [许可](LICENSE) · [材料使用说明](NOTICE.md)
