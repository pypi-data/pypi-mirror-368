import numpy as np
import statsmodels.api as sm
from scipy.stats import norm


def get_citl(result_df, outcome_col, LP_col, level=0.95):
    # Set the confidence level and calculate the Z-score
    # scipy.stats.norm.ppf is the equivalent of qnorm in R
    z_val = norm.ppf(1 - (1 - level) / 2)

    # Build the model of calibration in the large (outcome ~ offset(linear predictor))
    citl_model = sm.GLM(
        result_df[outcome_col],
        np.ones(len(result_df)),
        family=sm.families.Binomial(),  # Binomial family with logit link
        offset=result_df[LP_col],
    )

    citl_result = citl_model.fit()

    # Calibration in the large (the intercept)
    citl = citl_result.params.iloc[0]
    # Standard error
    citl_se = citl_result.bse.iloc[0]
    # Calculate the lower and upper bounds of the confidence interval
    citl_lower = citl - z_val * citl_se
    citl_upper = citl + z_val * citl_se

    results = {
        "citl": citl,
        "citl_se": citl_se,
        "citl_lower": citl_lower,
        "citl_upper": citl_upper,
    }

    return results


def get_cal_slope(result, outcome_col, LP_col, level=0.95):
    # Set the confidence level and calculate the Z-score
    # scipy.stats.norm.ppf is the equivalent of qnorm in R
    z_val = norm.ppf(1 - (1 - level) / 2)

    # Build the model of calibration slope (outcome ~ linear predictor)
    slope_model = sm.GLM(
        result[outcome_col],
        sm.add_constant(result[LP_col]),
        family=sm.families.Binomial(),
    )

    slope_result = slope_model.fit()

    # Calibration in the large (the intercept)
    slope = slope_result.params.iloc[1]
    # Standard error
    slope_se = slope_result.bse.iloc[1]
    # Calculate the lower and upper bounds of the confidence interval
    slope_lower = slope - z_val * slope_se
    slope_upper = slope + z_val * slope_se

    results = {
        "cal_slope": slope,
        "cal_slope_se": slope_se,
        "cal_slope_lower": slope_lower,
        "cal_slope_upper": slope_upper,
    }

    return results


# ---- DeLong implementation (binary classification) ----
def compute_midrank(x):
    """Computes midranks."""
    J = np.argsort(x)
    Z = x[J]
    N = len(x)
    T = np.zeros(N, dtype=float)
    i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]:
            j += 1
        T[i:j] = 0.5 * (i + j - 1)
        i = j
    T2 = np.empty(N, dtype=float)
    T2[J] = T + 1
    return T2


def fastDeLong(predictions_sorted_transposed, label_1_count):
    """
    Fast DeLong implementation for AUC variance.
    """
    m = label_1_count
    n = predictions_sorted_transposed.shape[1] - m
    positive_examples = predictions_sorted_transposed[:, :m]
    negative_examples = predictions_sorted_transposed[:, m:]
    k = predictions_sorted_transposed.shape[0]

    tx = np.empty([k, m], dtype=float)
    ty = np.empty([k, n], dtype=float)
    for r in range(k):
        tx[r, :] = compute_midrank(positive_examples[r, :])
        ty[r, :] = compute_midrank(negative_examples[r, :])
    tz = np.empty([k, m + n], dtype=float)
    for r in range(k):
        tz[r, :] = compute_midrank(predictions_sorted_transposed[r, :])
    aucs = tz[:, :m].sum(axis=1) / (m * n) - (m + 1) / (2.0 * n)

    v01 = (tx - tx.mean(axis=1)[:, None]) / n
    v10 = 1.0 - (ty - ty.mean(axis=1)[:, None]) / m - tx.mean(axis=1)[:, None] / n
    sx = np.cov(v01)
    sy = np.cov(v10)
    delongcov = sx / m + sy / n
    return aucs, delongcov


def get_auc(result, outcome_col, probability_col, level=0.95):
    """
    Get AUC and its confidence interval.
    """
    outcome = np.array(result[outcome_col])
    probabilities = np.array(result[probability_col])

    # sort by outcome so that positives come first
    order = np.argsort(-outcome)  # 1's first
    outcome = outcome[order]
    probabilities = probabilities[order]

    label_1_count = np.sum(outcome == 1)

    # shape: classifiers x examples
    preds = np.expand_dims(probabilities, axis=0)

    aucs, delongcov = fastDeLong(preds, int(label_1_count))
    auc = aucs[0]

    auc_var = delongcov if np.isscalar(delongcov) else delongcov[0, 0]
    std = np.sqrt(auc_var)

    z = norm.ppf(1 - (1 - level) / 2)
    ci_lower = auc - z * std
    ci_upper = auc + z * std

    results = {
        "auc": auc,
        "auc_se": std,
        "auc_lower": ci_lower,
        "auc_upper": ci_upper,
    }

    return results


def rubins_rule_pooling(estimates, variances):
    """
    使用Rubin's rule计算多重插补的pooled结果

    Parameters:
    estimates: array-like, 各个插补数据集的估计值
    variances: array-like, 各个插补数据集的方差 (SE^2)

    Returns:
    dict: 包含pooled估计值、SE、置信区间等
    """
    estimates = np.array(estimates)
    variances = np.array(variances)

    m = len(estimates)  # 插补数据集数量

    # Step 1: Pooled estimate (平均值)
    pooled_estimate = np.mean(estimates)

    # Step 2: Within-imputation variance (平均方差)
    within_var = np.mean(variances)

    # Step 3: Between-imputation variance (估计值间的方差)
    between_var = np.var(estimates, ddof=1) if m > 1 else 0

    # Step 4: Total variance
    total_var = within_var + (1 + 1 / m) * between_var
    pooled_se = np.sqrt(total_var)

    # Step 5: Degrees of freedom
    if between_var > 0:
        lambda_val = (1 + 1 / m) * between_var / total_var
        df = (m - 1) * (1 + within_var / ((1 + 1 / m) * between_var)) ** 2
    else:
        df = np.inf

    # Step 6: 95% 置信区间 (使用t分布)
    from scipy import stats

    if df == np.inf:
        t_critical = stats.norm.ppf(0.975)
    else:
        t_critical = stats.t.ppf(0.975, df)

    ci_lower = pooled_estimate - t_critical * pooled_se
    ci_upper = pooled_estimate + t_critical * pooled_se

    return {
        "pooled_estimate": pooled_estimate,
        "pooled_se": pooled_se,
        "within_var": within_var,
        "between_var": between_var,
        "total_var": total_var,
        "df": df,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


# 应用Rubin's rule到数据
def pool_metrics(validation_df, metrics=["citl", "cal_slope", "auc"]):
    """计算所有指标的pooled结果"""

    # 去除有错误的行
    valid_df = validation_df.dropna()

    results = {}

    for metric in metrics:
        estimates = valid_df[f"{metric}"].values
        variances = (valid_df[f"{metric}_se"].values) ** 2
        results[metric] = rubins_rule_pooling(estimates, variances)

    return results


if __name__ == "__main__":
    # --- Example Usage ---
    # In a real scenario, this DataFrame would come from your model's predictions
    import pandas as pd

    pred_results = pd.DataFrame(
        {
            "LP_col": np.random.randint(0, 2, size=200),
            "linear_predictor": np.random.randn(200) * 0.4 - 0.2,
        }
    )
