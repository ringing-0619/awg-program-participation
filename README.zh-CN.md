# AWG 零售项目参与分析

[English](README.md) | 简体中文

本项目是 **UIUC BADM550 的客户分析项目**，围绕 AWG 零售支持项目开展数据分析与评估。

**Python · pandas · NumPy · statsmodels · Matplotlib · seaborn · Excel**

## 项目概览

- **项目背景：**AWG 通过 AIM 自动配货与 One Source 店内陈列支持新品上市。
- **数据范围：** **54万+条月度销售记录**，以及门店参与名单、商品属性和上市日期数据。
- **业务问题：**不同项目参与组的新品采购与门店覆盖表现有何差异？这些差异如何随**品牌和区域**变化？

## 我的贡献

- **数据处理：**处理 **54万+条原始记录**，完成长表转换、数据清洗、模糊匹配与多表整合，明确**门店 × 商品 × 年月**的基础分析粒度。[代码](notebooks/01_checkpoint1_data_and_metrics.ipynb)
- **指标构建 · Checkpoint 1：**围绕不同参与组的新品表现，编写 Python 按**门店 × 上市批次**计算**上市次月起3个月的累计销售额和开票数量**，并计算**商品级门店覆盖率**。[代码](notebooks/01_checkpoint1_data_and_metrics.ipynb)
- **回归分析 · Checkpoint 2：**使用 Python 构建**项目 × 品牌 OLS交互回归模型**，通过可视化比较 **5个品牌**在不同参与组的累计销售表现。[代码](notebooks/02_checkpoint2_brand_and_division.ipynb)
- **客户汇报：**制作并讲解两轮汇报中的指标设计、回归方法与品牌分析成果。[第一轮第3–7页](presentations/checkpoint-1-client-presentation.pptx) · [第二轮第17–19页](presentations/checkpoint-2-client-presentation.pptx)

## 关键发现

- 第一轮比较中，同时参加两项项目的门店组，**每店平均早期销售额最高**。
- 品牌与区域分析呈现各自的项目表现，形成**品牌定向建议和区域试点优先方向**，并通过两轮客户汇报交付。

**指标设计 — 第一轮第5页**

![原客户汇报：按门店和上市批次汇总的三个月销售额与开票数量](reports/presentation-excerpts/historical_checkpoint1_sales_metrics.png)

**品牌比较 — 第二轮第19页**

![不同品牌与项目参与类别的累计销售对数均值](reports/presentation-excerpts/historical_brand_program_log_sales.png)

## 项目内容

| 内容 | 文件入口 |
|---|---|
| 数据处理与指标计算 | [第一轮 notebook](notebooks/01_checkpoint1_data_and_metrics.ipynb) · [指标定义](docs/methodology.md) |
| 品牌与区域分析 | [第二轮 notebook](notebooks/02_checkpoint2_brand_and_division.ipynb) · [完整成果](docs/checkpoint-2.zh-CN.md) |
| 客户交付物 | [两份完整汇报](presentations/README.md) · [原项目图表](reports/presentation-excerpts/README.md) |

客户工作簿保存在本地，环境配置与输入要求见[运行说明](docs/reproducibility.md)。

[完整案例](docs/case-study.md) · [项目交付](docs/project-deliverables.md) · [原始代码归档](notebooks/archive/README.md) · [许可](LICENSE) · [材料使用说明](NOTICE.md)
