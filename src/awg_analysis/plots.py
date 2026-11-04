"""Static evidence charts for local project analysis."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "#fafaf7", "axes.facecolor": "#fafaf7"})


def save_figures(metrics, support, contrasts, output, label):
    output.mkdir(parents=True, exist_ok=True)
    summary = metrics["program_3m"].sort_values("mean_sales_3m")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    axes[0].barh(summary.program, summary.n_stores, color="#244b5a")
    axes[0].set_xlabel("Stores in the declared roster")
    axes[0].set_title("Group sizes define the denominator")
    axes[1].barh(summary.program, summary.mean_sales_3m, color="#ba713d")
    axes[1].set_xlabel("Mean net 3-month sales per roster store ($)")
    axes[1].set_title("Compare normalized sales")
    fig.suptitle(f"Participation and early sales | {label}", fontsize=14)
    fig.savefig(output / "participation_and_3m_sales.png", dpi=170)
    plt.close(fig)
    counts = support.pivot(index="division", columns="program", values="n_stores").fillna(0)
    fig, ax = plt.subplots(figsize=(12, 4.8), constrained_layout=True)
    im = ax.imshow(counts.values, cmap="Blues", vmin=0)
    ax.set_xticks(range(len(counts.columns)), counts.columns, rotation=22, ha="right")
    ax.set_yticks(range(len(counts)), counts.index)
    for i in range(len(counts)):
        for j in range(len(counts.columns)):
            v = counts.iloc[i, j]
            ax.text(j, i, str(int(v)), ha="center", va="center",
                    color="white" if v > counts.values.max() * 0.6 else "#163b49")
    ax.set_title(f"Independent store support by division and program | {label}", pad=12)
    fig.colorbar(im, ax=ax, label="Distinct stores")
    fig.savefig(output / "division_program_support.png", dpi=170)
    plt.close(fig)
    if not contrasts.empty:
        # Display the preselected comparison across every supported division.
        plot = contrasts.loc[contrasts.program.eq("AIM_A & One Source")].sort_values("division")
        if not plot.empty:
            fig, ax = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
            y = np.arange(len(plot))
            ax.errorbar(plot.log1p_difference, y,
                        xerr=np.vstack([plot.log1p_difference-plot.ci_low,
                                        plot.ci_high-plot.log1p_difference]),
                        fmt="o", color="#244b5a", capsize=4)
            ax.axvline(0, color="#8a8a82", linestyle="--", linewidth=1)
            ax.set_yticks(y, plot.division)
            ax.set_xlabel("Difference in mean log(1 + source m12 sales), with 95% CI")
            ax.set_title(f"AIM_A + One Source versus None | {label}")
            fig.savefig(output / "division_contrasts.png", dpi=170)
            plt.close(fig)
