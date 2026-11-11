"""A consistent set of static, exportable charts. No dashboard framework needed."""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter

NAVY = "#17324D"
TEAL = "#16897F"
CORAL = "#D86B52"
GREY = "#65758A"


def configure_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.titlesize": 16, "axes.titleweight": "bold", "axes.titlepad": 18,
        "text.color": NAVY, "axes.labelcolor": GREY, "xtick.color": GREY,
        "ytick.color": GREY, "axes.edgecolor": "#DCE3EA",
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "grid.color": "#E8EDF1",
    })


def save_chart(fig, path):
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_charts(tables, metrics, output_dir):
    """Build six charts from the same summary tables used in the notebook/report."""
    configure_style()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    monthly = tables["monthly_sales"].loc["2017-01":"2018-08"]
    x = np.arange(len(monthly))
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 6.5), sharex=True,
                             gridspec_kw={"height_ratios": [2, 1]}, layout="constrained")
    axes[0].plot(x, monthly["product_sales"] / 1000, color=TEAL, linewidth=2.8, marker="o", markersize=4)
    axes[0].set_title("Monthly product sales and delivered order volume", loc="left")
    axes[0].set_ylabel("Product sales (R$ thousand)")
    axes[0].grid(axis="y")
    axes[1].bar(x, monthly["orders"], color=NAVY, width=.65)
    axes[1].set_ylabel("Orders")
    axes[1].set_xticks(x[::2], [str(p) for p in monthly.index[::2]])
    axes[1].yaxis.set_major_formatter(FuncFormatter(lambda value, pos: f"{value / 1000:g}k"))
    axes[1].set_xlabel("Purchase month · delivered orders only · Jan 2017–Aug 2018")
    save_chart(fig, output_dir / "01_monthly_sales.png")

    cat = tables["category_sales"].head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(11.5, 6), layout="constrained")
    labels = [c.replace("_", " ") for c in cat.index]
    ax.barh(labels, cat["product_sales"] / 1e6, color=TEAL, height=.65)
    ax.set_title("Top 10 categories by product sales", loc="left")
    ax.set_xlabel("Product sales (R$ million) · freight excluded")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    for idx, value in enumerate(cat["product_sales"] / 1e6):
        ax.text(value + .025, idx, f"{value:.2f}", va="center", fontsize=10)
    ax.set_xlim(0, (cat["product_sales"].max() / 1e6) * 1.15)
    save_chart(fig, output_dir / "02_category_sales.png")

    states = tables["state_performance"].query("eligible_deliveries >= 100").head(8).iloc[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.5), layout="constrained")
    axes[0].barh(states.index, states["late_orders"].astype(float), color=NAVY, height=.65)
    axes[0].set_title("Where late orders accumulate", loc="left")
    axes[0].set_xlabel("Late orders")
    axes[1].barh(states.index, states["late_rate_pct"].astype(float), color=CORAL, height=.65)
    axes[1].axvline(metrics["late_rate_pct"], color=GREY, linestyle="--", linewidth=1.3,
                    label=f"Overall {metrics['late_rate_pct']:.2f}%")
    axes[1].set_title("Volume and rate tell different stories", loc="left", fontsize=14)
    axes[1].set_xlabel("Late orders / eligible deliveries")
    axes[1].xaxis.set_major_formatter(PercentFormatter(100))
    axes[1].legend(frameon=False, loc="lower right", fontsize=10)
    for ax in axes:
        ax.grid(axis="x")
        ax.set_axisbelow(True)
    save_chart(fig, output_dir / "03_state_delivery.png")

    review = tables["delivery_reviews"]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.3), layout="constrained")
    colors = [TEAL, CORAL]
    axes[0].bar(review.index, review["average_score"], color=colors, width=.55)
    axes[0].set_title("Late orders receive lower scores", loc="left")
    axes[0].set_ylim(0, 5.5)
    axes[0].set_yticks(range(6))
    axes[0].set_ylabel("Average review score (1–5)")
    for idx, row in enumerate(review.itertuples()):
        axes[0].text(idx, row.average_score + .12,
                     f"{row.average_score:.2f}\nn = {row.reviewed_orders:,}", ha="center", fontsize=11)
    rates = review["low_score_rate_pct"].to_numpy()
    errors = np.vstack([rates - review["ci_low_pct"].to_numpy(), review["ci_high_pct"].to_numpy() - rates])
    axes[1].bar(review.index, rates, color=colors, width=.55,
                yerr=errors, capsize=5, error_kw={"ecolor": NAVY})
    axes[1].set_title("Low scores: 1 or 2 stars", loc="left")
    axes[1].set_ylim(0, max(80, rates.max() + 12))
    axes[1].yaxis.set_major_formatter(PercentFormatter(100))
    axes[1].set_ylabel("Share of eligible reviewed orders")
    for idx, value in enumerate(rates):
        axes[1].text(idx, value + 4, f"{value:.1f}%", ha="center")
    axes[1].set_xlabel("Error bars: 95% Wilson intervals; association, not causation", fontsize=9)
    save_chart(fig, output_dir / "04_delivery_reviews.png")

    # Month 0 is 100% by construction; excluding it makes small repeat rates legible.
    cohort = tables["cohort_retention_pct"].iloc[:, 1:7]
    fig, ax = plt.subplots(figsize=(11.5, 8), layout="constrained")
    cmap = plt.get_cmap("YlGnBu").copy()
    cmap.set_bad("#E9EDF1")
    image = ax.imshow(cohort.to_numpy(dtype=float), aspect="auto", cmap=cmap,
                       vmin=0, vmax=max(1, np.nanmax(cohort.to_numpy())))
    ax.set_xticks(range(6), [f"Month {m}" for m in range(1, 7)])
    sizes = tables["cohort_sizes"]["new_customers"]
    ax.set_yticks(range(len(cohort)), [f"{c}  ·  n={int(sizes.loc[c]):,}" for c in cohort.index])
    ax.set_title("Repeat purchasing is low across observed cohorts", loc="left")
    ax.set_ylabel("First observed delivered purchase month")
    ax.set_xlabel("Months since first purchase · cutoff: 31 Jul 2018 · grey = not yet observable")
    for row in range(len(cohort)):
        for col in range(6):
            value = cohort.iloc[row, col]
            if np.isfinite(value):
                ax.text(col, row, f"{value:.2f}%", ha="center", va="center", fontsize=9,
                        color="white" if value > image.get_clim()[1] * .6 else NAVY)
    colorbar = fig.colorbar(image, ax=ax, fraction=.025, pad=.03)
    colorbar.set_label("Customers purchasing again (%)")
    save_chart(fig, output_dir / "05_cohort_retention.png")

    sellers = tables["seller_performance"]
    cumulative = sellers["product_sales"].cumsum() / sellers["product_sales"].sum() * 100
    seller_share = np.arange(1, len(sellers) + 1) / len(sellers) * 100
    top20_idx = int(np.ceil(len(sellers) * .2)) - 1
    fig, ax = plt.subplots(figsize=(11.5, 5.5), layout="constrained")
    ax.plot(seller_share, cumulative, color=TEAL, linewidth=2.5)
    ax.plot([0, 100], [0, 100], color="#B8C4D1", linestyle="--", label="Equal sales per seller")
    ax.scatter(seller_share[top20_idx], cumulative.iloc[top20_idx], color=CORAL, zorder=3, s=55)
    ax.annotate(f"Top 20% of sellers: {cumulative.iloc[top20_idx]:.1f}% of sales",
                (seller_share[top20_idx], cumulative.iloc[top20_idx]),
                xytext=(34, 58), arrowprops={"arrowstyle": "-", "color": GREY}, fontsize=12)
    ax.set(xlim=(0, 100), ylim=(0, 103), xlabel="Delivered-order sellers ranked by product sales (%)",
           ylabel="Cumulative product sales (%)")
    ax.set_title("Sales depend on a relatively small group of sellers", loc="left")
    ax.grid(alpha=.6)
    ax.legend(frameon=False, loc="lower right")
    save_chart(fig, output_dir / "06_seller_concentration.png")
    return sorted(output_dir.glob("[0-9][0-9]_*.png"))
