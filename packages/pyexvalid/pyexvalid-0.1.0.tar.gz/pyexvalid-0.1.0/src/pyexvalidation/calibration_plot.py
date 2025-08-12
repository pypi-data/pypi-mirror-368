import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess


def cali_plot(
    outcomes,
    predictions,
    bin_num=10,
    max_scale=1,
    lowess_frac=0.5,
    figure_size=(8, 8),
    font_size=14,
    bar_bins=10,
):
    df = pd.DataFrame({"predictions": predictions, "outcomes": outcomes})

    df["bin"] = pd.qcut(df["predictions"], bin_num, duplicates="drop")

    bin_stats = (
        df.groupby("bin")
        .agg(
            mean_pred=("predictions", "mean"),
            mean_obs=("outcomes", "mean"),
            n=("predictions", "count"),
        )
        .dropna()
    )

    total_n = len(df)

    # --- Start plotting with GridSpec ---
    fig = plt.figure(figsize=figure_size)
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.05)

    # Calibration plot
    ax1 = fig.add_subplot(gs[0])
    sns.set_theme(style="whitegrid")

    ax1.scatter(
        bin_stats["mean_pred"], bin_stats["mean_obs"], color="blue", s=50, marker="x"
    )

    lowess_smoothed = lowess(
        endog=df["outcomes"],
        exog=df["predictions"],
        frac=lowess_frac,
        return_sorted=True,
    )
    ax1.plot(lowess_smoothed[:, 0], lowess_smoothed[:, 1], color="black")
    ax1.plot(
        [0, max_scale],
        [0, max_scale],
        linestyle="dashed",
        color="gray",
        label="Perfect calibration",
    )

    ax1.set_xlim(0, max_scale)
    ax1.set_ylim(0, max_scale)
    ax1.set_ylabel("Observed frequency", fontsize=font_size)
    ax1.set_title("Calibration Plot", fontsize=font_size)
    ax1.legend(fontsize=font_size)
    ax1.tick_params(axis="both", labelsize=font_size)
    ax1.tick_params(axis="x", which="both", bottom=True, top=True, labelbottom=False)

    # Histogram (%)
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    counts, bin_edges = np.histogram(
        df["predictions"], bins=bar_bins, range=(0, max_scale)
    )
    percentages = counts / total_n * 100
    bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
    bar_width = (max_scale / bar_bins) * 0.9

    ax2.bar(
        bin_centers, percentages, width=bar_width, color="lightgray", edgecolor="black"
    )
    ax2.set_xlim(0, max_scale)
    ax2.set_xlabel("Predicted probability", fontsize=font_size)
    ax2.set_ylabel("Percentage", fontsize=font_size)
    ax2.tick_params(axis="both", labelsize=font_size)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    import pandas as pd
    import numpy as np

    # Seed
    np.random.seed(42)

    # Random sample
    n_samples = 200
    predicted_risk = np.random.beta(a=2, b=5, size=n_samples)
    outcomes = np.random.binomial(n=1, p=predicted_risk)

    # Create DataFrame
    test_df = pd.DataFrame({"predictions": predicted_risk, "outcomes": outcomes})

    cali_plot(
        test_df["outcomes"],
        test_df["predictions"],
        bin_num=10,
        max_scale=1,
        lowess_frac=0.5,
        figure_size=(8, 6),
        font_size=14,
        bar_bins=50,
    )
